# openssh-ssh1 7.5p1

## Adaptation notes

- Uses the official OpenSSH portable 7.5p1 source archive.
- W0 dependencies are available in the `ohpcd` remote:
  - `zlib/1.3.1.1`
  - `openssl/3.5.6`
- Applies small Autotools portability patches for OHOS:
  - accept `linux-ohos` host triplets in `config.sub`;
  - avoid `umask 077` temporary directories that fail on OHOS HMDFS.
- Disables platform integrations not available in the OpenHarmony environment:
  sandbox, utmp/utmpx, wtmp/wtmpx, and lastlog.

## Tests

- Upstream: `make tests`, covering the 14 default OpenSSH regression targets
  declared by `REGRESS_TARGETS` in `regress/Makefile`.
- Consumer: `test_package` runs `ssh-keygen` to create an Ed25519 key pair and
  checks both private and public key files are non-empty.

