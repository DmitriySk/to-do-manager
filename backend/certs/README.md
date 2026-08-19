# Extra CA certificates for the build

Drop `*.crt` files (PEM) here and the image will trust them. Needed when local
antivirus or a corporate proxy intercepts TLS — otherwise `pip install` fails
with `CERTIFICATE_VERIFY_FAILED`.

Generate automatically:

```powershell
powershell -ExecutionPolicy Bypass -File ../../scripts/export-local-ca.ps1
```

The `.crt` files are git-ignored: they describe the machine, not the project.
An empty directory is fine — the build then just uses the default CA bundle.
