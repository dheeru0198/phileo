from django.core.urlresolvers import reverse
from django.db import models

from django.contrib.contenttypes.models import ContentType

from phileo.models import Like
from phileo.settings import LIKABLE_MODELS


def name(obj):
    return "%s.%s" % (obj._meta.app_label, obj._meta.object_name)


def _allowed(model):
    if isinstance(model, models.Model):
        app_model = name(model)
    elif isinstance(model, str):
        app_model = model
    else:
        app_model = str(model)
    return app_model in LIKABLE_MODELS


def get_config(obj):
    return LIKABLE_MODELS[name(obj)]


def widget_context(user, obj):
    ct = ContentType.objects.get_for_model(obj)
    config = get_config(obj)
    like_count = Like.objects.filter(
       receiver_content_type=ct,
       receiver_object_id=obj.pk
    ).count()
    if like_count == 1:
        counts_text = config["count_text_singular"]
    else:
        counts_text = config["count_text_plural"]
    
    can_like = user.has_perm("phileo.can_like", obj)
    
    ctx = {
        "can_like": can_like,
        "like_count": like_count,
        "counts_text": counts_text,
    }
    
    if can_like:
        liked = Like.objects.filter(
           sender=user,
           receiver_content_type=ct,
           receiver_object_id=obj.pk
        ).exists()
        
        if liked:
            like_text = config["like_text_on"]
            like_class = config["css_class_on"]
        else:
            like_text = config["like_text_off"]
            like_class = config["css_class_off"]
        
        ctx.update({
            "like_url": reverse("phileo_like_toggle", kwargs={
                "content_type_id": ct.id,
                "object_id": obj.pk
            }),
            "liked": liked,
            "like_text": like_text,
            "like_class": like_class
        })
    return ctx
