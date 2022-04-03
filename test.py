from django.core.cache import cache
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'kgproject.settings'
cache.set('current_graph', 'kg_name', None)
print(cache.get('current_graph'))