#!/usr/bin/env python
"""
Script para restaurar SOLO los datos desde backup.sql usando psql
Se ejecuta DESPUÉS de: python manage.py migrate
"""
import os
import sys
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings

def restore_data():
    backup_file = 'backup.sql'

    if not os.path.exists(backup_file):
        print(f"❌ No se encuentra {backup_file}")
        return False

    print("📦 Restaurando datos desde backup.sql usando psql...")

    db = settings.DATABASES['default']
    env = os.environ.copy()
    env['PGPASSWORD'] = db['PASSWORD']

    # Usar psql para restaurar directamente el archivo SQL
    cmd = [
        'psql',
        '-h', db['HOST'],
        '-p', str(db['PORT']),
        '-U', db['USER'],
        '-d', db['NAME'],
        '-f', backup_file,
        '-v', 'ON_ERROR_STOP=1'
    ]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Restauración completada con psql")
            return True
        else:
            print(f"⚠️  psql falló, intentando método alternativo...")
            print(f"stderr: {result.stderr[:500]}")
            return restore_data_alternative()
    except FileNotFoundError:
        print("⚠️  psql no encontrado, usando método alternativo...")
        return restore_data_alternative()
    except subprocess.TimeoutExpired:
        print("❌ Timeout en psql")
        return False

def restore_data_alternative():
    """Método alternativo: extraer solo INSERT statements"""
    import re
    from django.db import connection

    backup_file = 'backup.sql'
    print("📦 Método alternativo: convirtiendo COPY a INSERT...")

    with open(backup_file, 'r') as f:
        content = f.read()

    # El backup usa COPY ... FROM stdin; datos ... \.
    # Necesitamos convertir a INSERT
    # Buscar tablas y sus columnas
    copy_pattern = r'COPY public\.(\w+) \((.*?)\) FROM stdin;\n(.*?)\n\\.\n'
    matches = list(re.finditer(copy_pattern, content, re.DOTALL))

    print(f"📊 Encontradas {len(matches)} tablas con datos")

    with connection.cursor() as cursor:
        for match in matches:
            table = match.group(1)
            columns_str = match.group(2)
            data_block = match.group(3)

            columns = [c.strip() for c in columns_str.split(',')]
            col_list = ', '.join(f'"{c}"' for c in columns)

            # Parsear filas de datos (separadas por tabs)
            rows = []
            for line in data_block.strip().split('\n'):
                if line.strip():
                    values = line.split('\t')
                    rows.append(values)

            if not rows:
                print(f"  [{table}] 0 registros (vacío)")
                continue

            print(f"  [{table}] {len(rows)} registros")

            # Construir INSERTs en lotes
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                values_placeholders = ', '.join(['(' + ', '.join(['%s'] * len(columns)) + ')'] * len(batch))
                flat_values = [v for row in batch for v in row]

                # Convertir \N a NULL
                flat_values = [None if v == '\\N' else v for v in flat_values]

                sql = f'INSERT INTO public."{table}" ({col_list}) VALUES {values_placeholders} ON CONFLICT DO NOTHING'
                try:
                    cursor.execute(sql, flat_values)
                except Exception as e:
                    # Si falla por FK, intentar diferir constraints
                    if 'missing_components' in table or 'user_user_groups' in table or 'user_user_user_permissions' in table:
                        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
                        cursor.execute(sql, flat_values)
                    else:
                        print(f"    ❌ Error en {table}: {e}")
                        raise

    print("✅ Restauración alternativa completada")
    return True

if __name__ == '__main__':
    success = restore_data()
    sys.exit(0 if success else 1)