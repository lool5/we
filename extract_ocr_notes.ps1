$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and
    $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

function Wait-AsyncResult($Operation, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $task = $asTask.Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}

function Get-OcrText($Path) {
    $file = Wait-AsyncResult ([Windows.Storage.StorageFile]::GetFileFromPathAsync($Path)) ([Windows.Storage.StorageFile])
    $stream = Wait-AsyncResult ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    try {
        $decoder = Wait-AsyncResult ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Wait-AsyncResult ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
        if ($null -eq $engine) {
            return ""
        }
        $result = Wait-AsyncResult ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        return (($result.Text -replace "\s+", " ").Trim())
    }
    finally {
        $stream.Dispose()
    }
}

$root = (Get-Location).Path
$notes = [ordered]@{}
$images = Get-ChildItem -Recurse -File | Where-Object {
    $_.Extension -match "\.(jpg|jpeg|png)$" -and
    $_.DirectoryName -notmatch "Question|Qusetion|Questoin"
}

foreach ($image in $images) {
    $relative = $image.FullName.Substring($root.Length + 1).Replace("\", "/")
    try {
        $text = Get-OcrText $image.FullName
        if ($text) {
            $notes[$relative] = $text
        }
    }
    catch {
        $notes[$relative] = ""
    }
}

$json = $notes | ConvertTo-Json -Depth 4
Set-Content -LiteralPath "ocr-notes.json" -Value $json -Encoding UTF8
Write-Host "Generated OCR notes for $($notes.Count) images."
