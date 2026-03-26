from tortoise import fields, models


class TranslationCache(models.Model):
    id = fields.IntField(pk=True)
    source_text = fields.TextField()
    source_hash = fields.CharField(max_length=64, index=True)
    target_language = fields.CharField(max_length=16)
    translated_text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "translation_cache"
        unique_together = ("source_hash", "target_language")
