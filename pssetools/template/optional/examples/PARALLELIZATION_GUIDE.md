# Ejemplos de Configuración para Simulaciones en Paralelo

Esta carpeta contiene ejemplos de configuración YAML para ejecutar simulaciones en paralelo.

## Archivos de Ejemplo

### `config_accc_parallel.yml`
**Descripción**: Ejecuta 4 simulaciones ACCC de manera paralela usando 2 workers.

**Uso**:
```bash
pssetools sim-runner --config config_accc_parallel.yml
```

**Características**:
- 4 estudios ACCC para diferentes escenarios operativos
- Ejecución paralela con 2 procesos simultáneos
- Continúa ante errores desactivado (detiene en primer error)

**Configuración clave**:
```yaml
execution:
  parallel: 2  # Ejecuta 2 simulaciones a la vez
```

---

### `config_parallel_full.yml`
**Descripción**: Ejemplo completo con múltiples tipos de estudios (ACCC, ASCC, Dynamic) ejecutándose en paralelo con 4 workers.

**Uso**:
```bash
pssetools sim-runner --config config_parallel_full.yml
```

**Características**:
- 2 estudios ACCC
- 2 estudios ASCC
- 2 estudios Dynamic
- Ejecución paralela con 4 procesos
- Continúa ante errores activado (intenta completar todas las simulaciones)

**Configuración clave**:
```yaml
execution:
  parallel: 4  # Ejecuta 4 simulaciones simultáneamente
  continue_on_error: true  # Continúa incluso si falla alguna
```

---

## Notas sobre Parallelización

### Ventajas
✓ Mejor aprovechamiento de recursos (múltiples cores)
✓ Reducción del tiempo total de ejecución
✓ Ideal para análisis de múltiples escenarios

### Consideraciones
⚠️ Requiere suficiente memoria RAM (especialmente con PSS/E)
⚠️ Asegúrate de que cada simulación use archivos/directorios independientes
⚠️ No todas las operaciones de PSS/E son thread-safe

### Recomendaciones
- **parallel: 1 o 2**: Para laptops o sistemas con recursos limitados
- **parallel: 4**: Para workstations con 4+ cores
- **parallel: 8+**: Para servidores dedicados

---

## Parámetro `execution.parallel`

El parámetro `parallel` en la sección `execution` controla cuántos procesos se ejecutan simultáneamente:

| Valor | Comportamiento | Casos de Uso |
|-------|---|---|
| `1` | Secuencial (por defecto) | Servidores compartidos, depuración |
| `2-4` | Paralelo moderado | Laptops, PCs con múltiples cores |
| `8+` | Paralelo intensivo | Servidores, clusters |

---

## Adaptando estos Ejemplos

Para usar estos ejemplos en tu proyecto:

1. **Copiar y adaptar** uno de los archivos a tu proyecto
2. **Actualizar rutas** de casos, archivos .sub, .mon, .con, directorios de salida
3. **Ajustar parámetro `parallel`** según tu sistema
4. **Ejecutar en modo dry-run primero**:
   ```bash
   pssetools sim-runner --config tu_config.yml --dry-run
   ```
5. **Validar configuración** antes de ejecutar:
   ```bash
   pssetools sim-runner --config tu_config.yml --validate
   ```

---

## Troubleshooting

### Los procesos aún se ejecutan secuencialmente
- Verifica que `parallel: N` esté en la sección `execution` (no en `workspace`)
- Asegúrate de que N > 1

### Errores de memoria o PSS/E no responde
- Reduce el valor de `parallel` (ej: 2 en lugar de 4)
- Verifica que haya suficiente RAM disponible

### Una simulación falla y todo se detiene
- Usa `continue_on_error: true` en `execution` para continuar con otras

---

## Más Información

Ver también:
- `docs/SIM_RUNNER_GUIDE.md` - Guía completa del sim-runner
- `docs/PARAMETRIZATION_GUIDE.md` - Cómo evitar repetición en configuraciones
- `template/README.md` - Estructura general de plantillas
