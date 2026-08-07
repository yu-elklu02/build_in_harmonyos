# alass 2.0.0

Alass is a Rust workspace containing `alass-core` and `alass-cli`.

The recipe runs the three active upstream Rust unit tests with `cargo test --release --workspace`.

The consumer test aligns an offset SRT file to a reference SRT file and checks the corrected timestamp.

The initial HarmonyOS adaptation is restricted to armv8. True-device validation on ohos-aarch64 passed on 2026-08-07: all three Rust unit tests and the SRT synchronization consumer test succeeded.
