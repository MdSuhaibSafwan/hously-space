from rest_framework import serializers
from scraper.models import NetworkMonitoringAdvertisments
from django.core.files.storage import default_storage
from rest_framework import serializers
from decimal import Decimal

class NetworkMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkMonitoringAdvertisments
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        images = validated_data.pop('images', None)
        NetworkMonitoringAdvertisments = NetworkMonitoringAdvertisments.objects.create(user=user, **validated_data)

        if images:
            image_urls = []
            for image in images:
                path = default_storage.save(f'images/{image.name}', image)
                url = default_storage.url(path)
                image_urls.append(url)
            NetworkMonitoringAdvertisments.images = image_urls
            NetworkMonitoringAdvertisments.save()

        return NetworkMonitoringAdvertisments

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method == 'GET':
            target_currency = request.query_params.get('currency', instance.currency)
            ret['currency'] = target_currency
            if instance.currency == target_currency:
                ret['price'] = instance.price
            else:
                exchange_rate = self.get_exchange_rate(instance.currency, target_currency)
                if exchange_rate:
                    converted_price = Decimal(instance.price) * exchange_rate
                    ret['price'] = converted_price.quantize(Decimal('1.00'))
                else:
                    ret['price'] = instance.price
        return ret

    # def get_exchange_rate(self, base_currency, target_currency):
    #     if base_currency == target_currency:
    #         return Decimal('1.00')
    #     try:
    #         rate = ExchangeRate.objects.get(base_currency=base_currency, target_currency=target_currency).rate
    #         return rate
    #     except ExchangeRate.DoesNotExist:
    #         return None
