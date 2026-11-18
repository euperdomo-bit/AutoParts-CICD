Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](./LICENSE) para más detalles.
## Pipeline CI/CD

El workflow `.github/workflows/ci-cd.yml` se ejecuta en cada push a `develop` y en cada pull request a `main`:

1. **Build + Tests + Docker Scout**: construye la imagen, corre las pruebas unitarias dentro del contenedor y busca vulnerabilidades críticas.
2. **SonarCloud**: análisis estático de calidad (solo en PR a `main`).
3. **Snyk**: vulnerabilidades en dependencias y en el código (solo en PR a `main`).
4. **GitHub Advanced Security**: Dependency Review, escaneo de secretos (TruffleHog) y CodeQL.
5. **Publicar**: sube la imagen a Docker Hub solo si ningún control anterior falló.
