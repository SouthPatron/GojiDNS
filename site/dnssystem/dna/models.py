from django.db import models
from django.contrib.auth.models import User


class Profile( models.Model ):
	class Meta:
		pass

	user = models.OneToOneField( User, on_delete = models.CASCADE, related_name = 'dna_profile' )

