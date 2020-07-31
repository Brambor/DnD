from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entity(models.Model):
	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = _("Entities")

	name = models.CharField(
		max_length=200,
		unique=True,
	)
	group = models.CharField(
		max_length=200,
		blank=True,
	)
	hp_max = models.PositiveSmallIntegerField()
	mana_max = models.PositiveSmallIntegerField(
		default=0,
	)


class Skills(models.Model):
	class Meta:
		verbose_name_plural = _("Skills lists")

	entity = models.OneToOneField(
		Entity,
		on_delete=models.CASCADE
	)

	boj = models.SmallIntegerField(
		verbose_name=_("boj"),
		blank=True,
		null=True,
	)
	sila = models.SmallIntegerField(
		verbose_name=_("síla"),
		blank=True,
		null=True,
	)
	houzevnatost = models.SmallIntegerField(
		verbose_name=_("houževnatost"),
		blank=True,
		null=True,
	)
	remeslo = models.SmallIntegerField(
		verbose_name=_("řemeslo"),
		blank=True,
		null=True,
	)
	vira = models.SmallIntegerField(
		verbose_name=_("víra"),
		blank=True,
		null=True,
	)
	obratnost = models.SmallIntegerField(
		verbose_name=_("obratnost"),
		blank=True,
		null=True,
	)
	presnost = models.SmallIntegerField(
		verbose_name=_("přesnost"),
		blank=True,
		null=True,
	)
	plizeni = models.SmallIntegerField(
		verbose_name=_("plížení"),
		blank=True,
		null=True,
	)
	priroda = models.SmallIntegerField(
		verbose_name=_("příroda"),
		blank=True,
		null=True,
	)
	zrucnost = models.SmallIntegerField(
		verbose_name=_("zručnost"),
		blank=True,
		null=True,
	)
	magie = models.SmallIntegerField(
		verbose_name=_("magie"),
		blank=True,
		null=True,
	)
	intelekt = models.SmallIntegerField(
		verbose_name=_("intelekt"),
		blank=True,
		null=True,
	)
	znalosti = models.SmallIntegerField(
		verbose_name=_("znalosti"),
		blank=True,
		null=True,
	)
	vnimani = models.SmallIntegerField(
		verbose_name=_("vnímání"),
		blank=True,
		null=True,
	)
	charisma = models.SmallIntegerField(
		verbose_name=_("charisma"),
		blank=True,
		null=True,
	)


class Resistances(models.Model):
	class Meta:
		verbose_name_plural = _("Resistances lists")

	entity = models.OneToOneField(
		Entity,
		on_delete=models.CASCADE
	)

	acid = models.SmallIntegerField(
		default=0,
	)
	blunt = models.SmallIntegerField(
		default=0,
	)
	elemental = models.SmallIntegerField(
		default=0,
	)
	fire = models.SmallIntegerField(
		default=0,
	)
	ice = models.SmallIntegerField(
		default=0,
	)
	lightning = models.SmallIntegerField(
		default=0,
	)
	magic = models.SmallIntegerField(
		default=0,
	)
	necrotic = models.SmallIntegerField(
		default=0,
	)
	physical = models.SmallIntegerField(
		default=0,
	)
	piercing = models.SmallIntegerField(
		default=0,
	)
	poison = models.SmallIntegerField(
		default=0,
	)
	radiant = models.SmallIntegerField(
		default=0,
	)
	slashing = models.SmallIntegerField(
		default=0,
	)
	water = models.SmallIntegerField(
		default=0,
	)
	wind = models.SmallIntegerField(
		default=0,
	)
