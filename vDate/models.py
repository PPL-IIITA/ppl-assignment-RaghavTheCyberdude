from django.db import models
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import datetime
from .constants import *
from decimal import *
import math

"""
Created on 26 February 2017
.. module:: models
	:platform: Unix, Windows
	:synopsis: All the classes(models).
.. projectauthor:: Raghav Khandelwal <LIT2015002>
"""

class Girl(models.Model):
	"""
	Class representing the Girl Object with all its attributes
	"""
	name = models.CharField(max_length=100)
	attractiveness = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	intelligenceLevel = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	isCommitted = models.BooleanField(default=False)
	maintenanceBudget = models.DecimalField(max_digits=13, decimal_places=2)
	datingCriteria = models.IntegerField(choices=datingCriteriaChoices)
	girlType = models.IntegerField(choices=committedGirlTypes, default=None)
	
	def __str__(self):
		return self.name
		
	def commit(self):
		self.isCommitted = True
		self.save()

	def leave(self):
		self.isCommitted = False
		self.save()
	
class Boy(models.Model):
	"""
	Class representing the Boy Object with all its attributes
	"""
	name = models.CharField(max_length=100)
	attractiveness = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	intelligenceLevel = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	isCommitted = models.BooleanField(default=False)
	budget = models.DecimalField(max_digits=13, decimal_places=2)
	attractionRequirement = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	boyType = models.IntegerField(choices=committedBoyTypes, default=None)
	
	def __str__(self):
		return self.name
		
	def commit(self):
		self.isCommitted = True
		self.save()

	def leave(self):
		self.isCommitted = False
		self.save()

	def increaseBudget(self, increase):
		budget = budget + increase;


class EssentialGift(models.Model):
	"""
	Class representing the Essential Gift Object with all its attributes
	"""
	price = models.DecimalField(max_digits=13, decimal_places=2)
	value = models.FloatField()

	def __str__(self):
		return "Price: " + str(self.price) + ", Value: " + str(self.value)

class LuxuryGift(models.Model):
	"""
	Class representing the Luxury Gift Object with all its attributes
	"""
	price = models.DecimalField(max_digits=13, decimal_places=2)
	value = models.FloatField()
	luxuryRating = models.FloatField()
	difficultyToObtain = models.FloatField()

	def __str__(self):
		return "Price: " + str(self.price) + ", Value: " + str(self.value)

class UtilityGift(models.Model):
	"""
	Class representing the Utility Object with all its attributes
	"""
	price = models.DecimalField(max_digits=13, decimal_places=2)
	value = models.FloatField()
	utilityValue = models.FloatField()
	utilityClass = models.IntegerField(choices=utilityClasses)

	def __str__(self):
		return "Price: " + str(self.price) + ", Value: " + str(self.value)

class Relation(models.Model):
	"""
	Class representing the Relation Object with all its attributes, which represents the relation between committed boys and girls.
	Supports breakup and finding compatibility, happiness, etc.
	"""
	boy = models.ForeignKey(Boy, on_delete=models.CASCADE)
	girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
	commitOn = models.DateTimeField(default=timezone.now)
	breakupOn = models.DateTimeField(blank=True, null=True)
	compatibility = models.FloatField(default=0)
	happiness = models.FloatField(blank=True, null=True)

	def __str__(self):
		if self.breakupOn is None:
			return "%s + %s" % (self.girl.name, self.boy.name)
		return "%s was with %s" % (self.girl.name, self.boy.name)

	def breakup(self):
		"""
		Breaks up relationship. Sets girl and boy to not committed.

		:param self: Object of type Relation
		"""
		self.breakupOn = datetime.now()
		self.girl.leave()
		self.boy.leave()
		self.delete()

	def findCompatibility(self):
		"""
		Finds compatibility between girl and boy in a relationship.

		:param self: Object of type Relation
		"""
		self.compatibility = (self.boy.budget - self.girl.maintenanceBudget) + Decimal(abs(self.boy.attractiveness - self.boy.attractiveness)) + Decimal(abs(self.boy.intelligenceLevel - self.girl.intelligenceLevel))
		self.save()
		return self.compatibility

	def findHappiness(self):
		"""
		Calculates girl and boy happiness to find happiness of couple.

		:param self: Object of type Relation
		:returns: Happiness of couple
		"""
		total_cost = Decimal(0)
		gifts = self.exchanges.all()
		for gift in gifts:
			total_cost = total_cost + gift.getGift().price

		if self.girl.girlType == 1:
			for gift in gifts:
				if gift.giftType == 2:
					total_cost = total_cost + gift.getGift().price
			girlHappiness = math.log(abs(total_cost - self.girl.maintenanceBudget))
		elif self.girl.girlType == 2:
			for gift in gifts:
				total_cost = total_cost + Decimal(gift.getGift().value)
			girlHappiness = total_cost - self.girl.maintenanceBudget
		elif self.girl.girlType == 3:
			try:
				girlHappiness = math.exp(total_cost - self.girl.maintenanceBudget)
			except OverflowError:
				girlHappiness = float('inf')

		if self.boy.boyType == 1:
			boyHappiness = self.boy.budget - total_cost
		elif self.boy.boyType == 2:
			boyHappiness = girlHappiness
		elif self.boy.boyType == 3:
			boyHappiness = self.girl.intelligenceLevel

		self.happiness = float(boyHappiness) + float (girlHappiness)
		self.save()
		return self.happiness


class Exchange(models.Model):
	"""
	Class representing the Exchange Object with all its attributes.

	It models all the gift tranfers between the boy and the girl and the time stamp at which the exchange took place. Supports all 3 type of gifts.
	"""
	relation = models.ForeignKey('vDate.Relation', related_name='exchanges')
	essentialGift = models.ForeignKey('vDate.EssentialGift', blank=True, null=True)
	luxuryGift = models.ForeignKey('vDate.LuxuryGift', blank=True, null=True)
	utilityGift = models.ForeignKey('vDate.UtilityGift', blank=True, null=True)
	giftType = models.IntegerField(choices=giftTypes, default=None)
	exchangeTime = models.DateTimeField(default = timezone.now)

	def __str__(self):
		return "%s got gift worth %.2f from %s on %s" % (self.relation.girl.name, self.getGift().price, self.relation.boy.name, self.exchangeTime)

	def getGift(self):
		"""
		Returns the appropriate gift type.

		:param self: Object of type Exchange
		:returns: Type of gift in exchange 
		"""
		if self.giftType == 1:
			return self.essentialGift
		elif self.giftType == 2:
			return self.luxuryGift
		elif self.giftType == 3:
			return self.utilityGift
		else:
			return None