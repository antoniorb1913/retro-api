from django.db import models

class ItemBase(models.Model):
    STATUS_CHOICES = [
        ('SEALED', 'Prencitado'),
        ('MINT', 'Como nuevo'),
        ('GOOD', 'Buen estado'),
        ('FAIR', 'Desgastado'),
    ]
    
    name = models.CharField(
        'nombre',
        max_length=200
    )

    acquisition_date = models.DateField(
        'fecha de adquisición',
        null=True, 
        blank=True
    )

    price = models.DecimalField(
        'precio de compra',
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )

    status = models.CharField(
        'estado',
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='GOOD'
    )

    description = models.TextField(
        'descripción',
        max_length=255, 
        blank=True, 
        null = True
    )

    region = models.CharField(
        'region',
        max_length=10, 
        default='PAL', 
        blank = True, 
        null = True
    )

    it_has_a_box = models.BooleanField(
        '¿tiene caja?',
        default=False
    )
    
    complete = models.BooleanField(
        '¿completo?',
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Añadido el"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última modificación"
    )
    
    class Meta:
        abstract = True