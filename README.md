# Scripts
## Generate hexagons for city and extract road features
```python
python .\scripts\generate_place.py download 'Wrocław,Poland' .\data\generated\
python .\scripts\generate_place.py h3 .\data\generated\Wroclaw_Poland\place.geojson .\data\generated\Wroclaw_Poland 8
python .\scripts\generate_place.py assignh3 .\data\generated\Wroclaw_Poland
python .\scripts\generate_place.py features .\data\generated\Wroclaw_Poland
```

# Settings
## VSCode settings
```json
{
    "python.pythonPath": "venv\\Scripts\\python.exe",
    "python.formatting.provider": "black",
    "python.linting.pylintEnabled": true,
    "python.linting.enabled": true,
    "python.languageServer": "Pylance",
    "python.analysis.extraPaths": [
        "src"
    ],
    "terminal.integrated.env.windows": {
        "PYTHONPATH": ".;src"
    },
}
```