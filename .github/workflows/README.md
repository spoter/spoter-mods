### Принудительное обновление кэша
Чтобы переустановить Python 2.7 и зависимости:
1. Перед запуском workflow измените переменную в файле `.github/workflows/build-and-release__in_work.yml`:
   ```yaml
   env:
     FORCE_CACHE_REFRESH: "true"