from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Elimina logs de actividad con más de X días (default: 90)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias",
            type=int,
            default=90,
            help="Días de antigüedad máxima (default: 90)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra cuántos se borrarían sin borrar nada",
        )

    def handle(self, *args, **options):
        from client.models import ActivityLog

        dias    = options["dias"]
        dry_run = options["dry_run"]
        corte   = timezone.now() - timedelta(days=dias)

        logs_viejos = ActivityLog.objects.filter(fecha__lt=corte)
        total       = logs_viejos.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                f"No hay logs con más de {dias} días. Nada que limpiar."
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"[DRY RUN] Se borrarían {total} logs anteriores a {corte:%d/%m/%Y}."
            ))
            return

        logs_viejos.delete()
        self.stdout.write(self.style.SUCCESS(
            f"✅ {total} logs eliminados (anteriores a {corte:%d/%m/%Y})."
        ))