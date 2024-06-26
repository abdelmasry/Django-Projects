import logging
from io import BytesIO

from PIL import Image
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.db.models.signals import pre_save, post_save
from .models import ProductImage, Basket, OrderLine, Order

THUMBNAIL_SIZE = (300, 300)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(
        "Generating thumbnail for product %d",
        instance.product.id,
    )
    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)
    # set save=False, otherwise it will run in an infinite loop
    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()


@receiver(user_logged_in)
def merge_baskets_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None)
    if anonymous_basket:
        try:
            loggedin_basket = Basket.objects.get(user=user, status=Basket.OPEN)
            for line in anonymous_basket.basketline_set.all():
                line.basket = loggedin_basket
                line.save()
            anonymous_basket.delete()
            request.basket = loggedin_basket
            logger.info("Merged basket to id %d", loggedin_basket.id)
        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(
                "Assigned user to basket id %d",
                anonymous_basket.id,
            )


@receiver(post_save, sender=OrderLine)
def orderline_to_order_status(sender, instance, **kwargs):
    """This signal will be executed after saving instances of the OrderLine model. 
    The first thing it does is check whether any order lines connected to the order have statuses below “sent.” 
    If there is any, the execution is terminated. 
    If there is no line below the “sent” status, the whole order is marked as “done.”

    Args:
        sender (_type_): _description_
        instance (_type_): _description_
    """
    if not instance.order.lines.filter(status__lt=OrderLine.SENT).exists():
        logger.info(
            "All lines for order %d have been processed. Marking as done.",
            instance.order.id,
        )
        instance.order.status = Order.DONE
        instance.order.save()
