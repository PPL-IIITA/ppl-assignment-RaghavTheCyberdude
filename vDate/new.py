from .models import *
import random
from datetime import datetime
from vDate.names.name import get_full_name
"""
This module contains all the utility functions called by our project.
Generates random objects of all the classes as required by the specifications.
:Author: Raghav Khandelwal
:RollNo: LIT2015002
"""
def newRandomBoy():
	"""
	Generates a new Boy with random attributes
	"""
	name = get_full_name('male')
	attractiveness = random.triangular(attractionMin, attractionMax, attractionMode)
	intelligenceLevel = random.triangular(intelligenceMin, intelligenceMax, intelligenceMode)
	budget = random.triangular(budgetMin, budgetMax, budgetMode)
	attractionRequirement = random.triangular(attractionMin, attractionMax, attractionMode)
	boyType = random.randint(1,3)
	boy = Boy.objects.create(name=name, attractiveness=attractiveness, intelligenceLevel=intelligenceLevel, budget=budget, attractionRequirement=attractionRequirement, boyType=boyType)

def newRandomGirl():
	"""
	Generates a new Girl with random attributesl
	"""
	name = get_full_name('female')
	attractiveness = random.triangular(attractionMin, attractionMax, attractionMode)
	intelligenceLevel = random.triangular(intelligenceMin, intelligenceMax, intelligenceMode)
	maintenanceBudget = random.triangular(maintenanceBudgetMin, maintenanceBudgetMax, maintenanceBudgetMode)
	datingCriteria = random.randint(1,3)
	girlType = random.randint(1,3)
	Girl.objects.create(name=name, attractiveness=attractiveness, intelligenceLevel=intelligenceLevel, maintenanceBudget=maintenanceBudget, datingCriteria=datingCriteria, girlType=girlType)

def newEssentialGift():
	"""
	Generates a new Essential Gift with random attributes
	"""
	price =  random.triangular(giftMin, giftMax, giftMode)
	value = price
	EssentialGift.objects.create(price=price, value=value)

def newLuxuryGift():
	"""
	Generates a new Luxury Gift with random attributes
	"""
	price =  random.triangular(luxuryGiftMin, luxuryGiftMax, luxuryGiftMode)
	rating = random.triangular(ratingMin, ratingMax, ratingMode)
	difficultyToObtain = random.triangular(ratingMin, ratingMax, ratingMode)
	value = price * rating
	LuxuryGift.objects.create(price=price, value=value, luxuryRating=rating, difficultyToObtain=difficultyToObtain)

def newUtilityGift():
	"""
	Generates a new Utility Gift with random attributes
	"""
	price =  random.triangular(giftMin, giftMax, giftMode)
	utilityValue = random.triangular(ratingMin, ratingMax/2, ratingMode/2)
	utilityClass = random.randint(1,5)
	value = price * utilityValue
	UtilityGift.objects.create(price=price, value=value, utilityValue=utilityValue, utilityClass=utilityClass)

def findMatch(girl):
	"""
	Function finds an appropriate match for girl, after checking eligibility criterias and girls choice of boys.
	It then creates a new relationship if an appropriate match is found.

	:param girl: Object of type Girl whose match is to be found
	:returns: New Relation object if match is found, otherwise None
	"""
	if girl.isCommitted:
		return None
	boyList = Boy.objects.filter(isCommitted=False)
	if girl.datingCriteria == 1:
		boyList.order_by('attractiveness')
	if girl.datingCriteria == 2:
		boyList.order_by('budget')
	if girl.datingCriteria == 3:
		boyList.order_by('intelligence')
	for boy in boyList:
		if boy.isCommitted:
			continue
		if boy.budget >= girl.maintenanceBudget and girl.attractiveness >= boy.attractionRequirement:
			boy.commit()
			girl.commit()
			newRelation = Relation(boy=boy, girl=girl, commitOn=datetime.now())
			newRelation.findCompatibility()
			newRelation.save(force_insert=True)
			return newRelation
	return None

def breakupAll():
	"""
	Utility function used to breakup all the relationships.
	"""
	for relation in Relation.objects.all():
		relation.breakup()

def performGifting(relation):
	"""
	Main objective of this function is to perform the gifting between a couple.
	Depending on the type of boy, it performs greedy search to find the best possible and fitting gift, and creates a new instance of exchange to model the gifting that took place. TimeStamp is incorporated for debugging purposes.

	:param relation: Relation for which gifting is to be done. 
	"""
	essential = EssentialGift.objects.all().order_by('price')
	luxury = LuxuryGift.objects.all().order_by('price')
	utility = UtilityGift.objects.all().order_by('price')
	ef = essential.count()
	lf = luxury.count()
	uf = utility.count()
	if relation.boy.boyType == 1:
		total_spent = 0
		e = 0
		u = 0
		l = 0
		while total_spent <= relation.girl.maintenanceBudget and e<ef and u<uf and l<lf:
			if essential[e].price < utility[u].price and essential[e].price < luxury[l].price and e<ef and u<uf and l<lf:
				total_spent += essential[e].price
				Exchange.objects.create(relation=relation, giftType=1, essentialGift=essential[e], exchangeTime=datetime.now())
				e = e+1
			elif luxury[l].price < utility[u].price and luxury[l].price < essential[e].price and e<ef and u<uf and l<lf:
				total_spent += luxury[l].price
				Exchange.objects.create(relation=relation, giftType=2, luxuryGift=luxury[l], exchangeTime=datetime.now())
				l = l+1
			elif e<ef and u<uf and l<lf:
				total_spent += utility[u].price
				Exchange.objects.create(relation=relation, giftType=3, utilityGift=utility[u], exchangeTime=datetime.now())
				u = u+1
			else:
				break
	elif relation.boy.boyType == 2:
		total_left = relation.boy.budget
		e = ef-1
		u = uf-1
		l = lf-1
		while total_left >= 0 and e>=0 and u>=0 and l>=0:
			if essential[e].price > utility[u].price and essential[e].price > luxury[l].price and e>=0 and u>=0 and l>=0:
				total_left -= essential[e].price
				if total_left < essential[e].price:
					break
				Exchange.objects.create(relation=relation, giftType=1, essentialGift=essential[e], exchangeTime=datetime.now())
				e = e-1
			elif luxury[l].price > utility[u].price and luxury[l].price > essential[e].price  and e>=0 and u>=0 and l>=0:
				total_left -= luxury[l].price
				if total_left < luxury[l].price:
					break
				Exchange.objects.create(relation=relation, giftType=2, luxuryGift=luxury[l], exchangeTime=datetime.now())
				l = l-1
			elif e>=0 and u>=0 and l>=0:
				total_left -= utility[u].price
				if total_left < utility[u].price:
					break
				Exchange.objects.create(relation=relation, giftType=3, utilityGift=utility[u], exchangeTime=datetime.now())
				u = u-1
			else:
				break

	elif relation.boy.boyType == 3:
		total_spent = 0
		e = 0
		u = 0
		l = 0
		while total_spent <= relation.girl.maintenanceBudget and e<ef and u<uf and l<lf:
			if essential[e].price < utility[u].price and essential[e].price < luxury[l].price and e<ef and u<uf and l<lf:
				total_spent += essential[e].price
				Exchange.objects.create(relation=relation, giftType=1, essentialGift=essential[e], exchangeTime=datetime.now())
				e = e+1
			elif luxury[l].price < utility[u].price and luxury[l].price < essential[e].price and e<ef and u<uf and l<lf:
				total_spent += luxury[l].price
				Exchange.objects.create(relation=relation, giftType=2, luxuryGift=luxury[l], exchangeTime=datetime.now())
				l = l+1
			elif e<ef and u<uf and l<lf:
				total_spent += utility[u].price
				Exchange.objects.create(relation=relation, giftType=3, utilityGift=utility[u], exchangeTime=datetime.now())
				u = u+1
			else:
				break
		if luxury[0].price < relation.boy.budget - total_spent:
			Exchange.objects.create(relation=relation, giftType=2, luxuryGift=luxury[0], exchangeTime=datetime.now())