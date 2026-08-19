<#
.SYNOPSIS
  Exports the root CA that terminates TLS on this machine into the Docker build
  contexts, so `pip install` / `npm install` work inside containers.

.DESCRIPTION
  Local antivirus / corporate proxies (e.g. Norton "Web/Mail Shield") re-sign
  every HTTPS connection with their own root CA. The Windows host trusts it,
  a fresh Linux container does not — builds then fail with
  CERTIFICATE_VERIFY_FAILED.

  The script walks the live TLS chain to pypi.org, takes the root, and writes it
  as PEM into backend/certs/ and frontend/certs/. Both Dockerfiles pick up any
  *.crt found there. The files are git-ignored: they describe this machine, not
  the project. On a machine without interception the chain root is a normal
  public CA and adding it changes nothing.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/export-local-ca.ps1
#>

param(
    [string]$TestHost = "pypi.org",
    [int]$Port = 443
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$targets = @(
    (Join-Path $repoRoot "backend\certs"),
    (Join-Path $repoRoot "frontend\certs")
)

$tcp = New-Object System.Net.Sockets.TcpClient($TestHost, $Port)
try {
    $ssl = New-Object System.Net.Security.SslStream($tcp.GetStream(), $false, { param($s, $c, $ch, $e) $true })
    $ssl.AuthenticateAsClient($TestHost)
    $leaf = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
    $ssl.Close()
}
finally {
    $tcp.Close()
}

$chain = New-Object System.Security.Cryptography.X509Certificates.X509Chain
$null = $chain.Build($leaf)
$root = $chain.ChainElements[$chain.ChainElements.Count - 1].Certificate

Write-Host "TLS chain root for ${TestHost}:"
Write-Host "  $($root.Subject)"
Write-Host "  thumbprint $($root.Thumbprint)"

$base64 = [Convert]::ToBase64String($root.RawData, "InsertLineBreaks")
$pem = "-----BEGIN CERTIFICATE-----`n$base64`n-----END CERTIFICATE-----`n"

foreach ($dir in $targets) {
    if (-not (Test-Path $dir)) { $null = New-Item -ItemType Directory -Path $dir }
    $file = Join-Path $dir "local-root-ca.crt"
    # LF endings and no BOM: the file is read by OpenSSL inside Linux containers.
    [IO.File]::WriteAllText($file, $pem, (New-Object Text.UTF8Encoding($false)))
    Write-Host "wrote $file"
}

Write-Host ""
Write-Host "Now rebuild: docker compose build --no-cache backend"
