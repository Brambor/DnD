from django.contrib import admin

from .models import Entity, Skills, Resistances


class SkillsInline(admin.StackedInline):
	model = Skills

class ResistancesInline(admin.StackedInline):
	model = Resistances

class EntityAdmin(admin.ModelAdmin):
	inlines = (
		SkillsInline,
		ResistancesInline,
	)
admin.site.register(Entity, EntityAdmin)
