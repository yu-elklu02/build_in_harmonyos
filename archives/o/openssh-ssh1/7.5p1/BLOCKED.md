# openssh-ssh1 7.5p1 — 真机验证阻塞报告

## 状态

**BLOCKED** — 编译阶段失败，需 codex 修复后才能继续真机验证。

## 验证环境

- 真机：elklu02/build_in_harmonyos（gitcode）
- 验证分支：`codex/openssh-ssh1-7.5p1-validate`
- 验证提交：`229b26ca5a8ffa2f2d77b7074937400953d52693`
- profile：`ci/conan/profiles/ohos-aarch64`
- conan：2.29.1
- target：OHOS 6.0 / armv8 / clang 15

## 阻塞点

### 1. AutotoolsToolchain 在 OHOS 上不自动注入 `--build`/`--host` triplet

**症状：**
```
configure: error: cannot guess build type; you must specify one
```

**根因：**
`conanfile.py` 的 `generate()` 用 `AutotoolsToolchain(self)`，期望 conan 自动注入 triplet。但 OHOS profile 下 `AutotoolsToolchain` 不注入 `--build`/`--host`，上游 `config.sub` 又不认 HarmonyOS `uname -s` 输出，导致 configure 猜不出 host 类型。

**真机已修：**
在 `tc.configure_args` 显式加：
```python
"--build=aarch64-linux-ohos",
"--host=aarch64-linux-ohos",
```
配合现有 `0001-config.sub-ohos.patch`（让 config.sub 接受 `linux-ohos` triplet）。

修复后 configure 通过，进入编译阶段。

### 2. OpenSSH 7.5p1 直接 deref RSA/DSA 结构成员，OpenSSL 1.1.1w 结构不透明

**症状：**
```
sshkey.c:278:28: error: incomplete definition of type 'struct rsa_st'
                return BN_num_bits(k->rsa->n);
                                   ~~~~~~^
openssl/ossl_typ.h:110:16: note: forward declaration of 'struct rsa_st'
typedef struct rsa_st RSA;
               ^
```

163 处直接 deref，分布在 7 个 .c 文件：

| 文件 | 直接 deref 处 |
|---|---|
| sshkey.c | 104 |
| sshconnect1.c | 22 |
| ssh-agent.c | 13 |
| ssh-keygen.c | 11 |
| authfd.c | 9 |
| ssh-keyscan.c | 2 |
| ssh-rsa.c | 2 |
| **总计** | **163** |

**根因（codex 认知错误）：**

`notes.md` 第 15-18 行写：
> Uses OpenSSL 1.1.1w because OpenSSH 7.5p1 directly accesses OpenSSL RSA,
> DSA, and EVP internals. OpenSSL 3.x makes those structures opaque and is
> not source-compatible with this SSH1-capable release without a large
> migration backport.

`manifest.yaml` 的 `knowledge_gained` 第 4 条：
> "OpenSSH 7.5p1 requires OpenSSL 1.1.1 APIs; OpenSSL 3.x opaque structs
> are incompatible without a large backport."

**这个认知是错的。** OpenSSL 1.1.0 就已经把 RSA/DSA 结构变成不透明了——1.1.1w 同样不透明。codex 误以为"用 1.1.1w 就能让 7.5p1 直接 deref 结构成员"，实际上 1.1.1w 强制要求用 `RSA_get0_key()` / `DSA_get0_pqg()` 等 accessor。

事实核查：
- `openssl/1.1.1w` 在 ohpcd ✅ 有，armv8/clang15
- `struct rsa_st` 在 1.1.1w 公开头文件里**完全没有定义**（只有 `typedef struct rsa_st RSA;` forward declaration），结构体藏在 OpenSSL 内部的 `rsa_locl.h` 里，不对外暴露
- `OPENSSL_API_COMPAT` 守护 deprecated 宏和 `<openssl/bn.h>` include，**不重新暴露结构成员**
- accessor 在 libcrypto.a ✅（`RSA_get0_key`/`RSA_get0_n`/`DSA_get0_key` 等）
- accessor 在 rsa.h/dsa.h ✅ 全部声明
- 7.5p1 用 accessor ❌ 0 处，163 处直接 deref

**路径 B 知识库拓展不可行：** `struct rsa_st` 对编译器不可见（只有 forward declaration），任何 `k->rsa->n` 在预处理后仍然是直接成员访问，编译器因结构体不完整而报 `incomplete definition`。无法用宏或 wrapper 头文件把 `k->rsa->n` 重写成 accessor——结构不可见，宏重写无效。

## 修复路径（路径 A：backport accessor 改造）

OpenSSH 上游在 7.9p1 完成 accessor 改造（27 处 `RSA_get0_*`/`DSA_get0_*`，0 处直接 deref）。7.6p1/7.7p1/7.7p1/7.8p1 都还没改（accessors=0）。

**改造模式（参考 7.9p1）：**

只读场景 — 用 getter accessor：
```c
/* 7.5p1（直接 deref，1.1.x 编不过）*/
return BN_num_bits(k->rsa->n);

/* 7.9p1（accessor）*/
const BIGNUM *rsa_n;
RSA_get0_key(k->rsa, &rsa_n, NULL, NULL);
return BN_num_bits(rsa_n);
```

赋值场景 — 用 setter accessor：
```c
/* 7.5p1（bn_maybe_alloc_failed 宏内部 p = BN_new() 直接写成员）*/
if (bn_maybe_alloc_failed(k->rsa->d) ||
    bn_maybe_alloc_failed(k->rsa->iqmp) || ...)

/* 7.9p1（用 RSA_set0_key/RSA_set0_factors 等 setter）*/
if (!RSA_set0_key(k->rsa, rsa_n, rsa_e, rsa_d)) ...
if (!RSA_set0_factors(k->rsa, rsa_p, rsa_q)) ...
```

**建议新增 patch：** `patches/0003-openssl-1.1-accessors.patch`，覆盖上述 7 个 .c 文件的 163 处直接 deref，改造为 accessor 调用。`conandata.yml` 注册该 patch。

**参考版本：** OpenSSH 7.9p1（commit 在 `openssh-portable` 仓库 `V_7_9_P1` tag）。

## 真机已做的修复（在验证分支工作区，未提交）

1. `conanfile.py` 的 `generate()` 显式加 `--build=aarch64-linux-ohos` / `--host=aarch64-linux-ohos`（修复阻塞点 1）
2. 本 BLOCKED.md 文件

## 真机未做的修复（需 codex 处理）

1. 阻塞点 2 的 accessor backport 改造（路径 A）
2. 改造后重跑 `conan create` 真机验证
3. 验证上游 `make tests` 是否能跑（accessor 改造后）

## 正式分支状态

`feat/openssh-ssh1-7.5p1`：**未被修改**。

## 给 codex 的行动项

1. **修正 `notes.md` 和 `manifest.yaml` 的 knowledge_gained**：OpenSSL 1.1.0+ 就已经把 RSA/DSA 结构变成不透明，不是 3.x 才不透明。1.1.1w 同样要求 accessor。
2. **新增 `patches/0003-openssl-1.1-accessors.patch`**：backport OpenSSH 7.9p1 的 accessor 改造到 7.5p1，覆盖 7 个 .c 文件的 163 处直接 deref。
3. **`conandata.yml` 注册该 patch**。
4. **`conanfile.py` 的 `generate()` 显式注入 `--build`/`--host` triplet**（修复阻塞点 1，真机已改但未提交，codex 可参考）。
5. **重跑真机验证**：`conan create` + 上游 `make tests` + test_package 功能断言。
