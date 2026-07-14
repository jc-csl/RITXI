$urls = @(
    'http://127.0.0.1:7860',
    'http://127.0.0.1:7860/docs',
    'http://127.0.0.1:8000/docs'
)

foreach ($url in $urls) {
    Start-Process $url
}