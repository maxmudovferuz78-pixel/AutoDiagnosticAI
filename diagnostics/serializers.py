from rest_framework import serializers

class AnalyzeDTCInputSerializer(serializers.Serializer):
    car_model = serializers.CharField(required=False, allow_blank=True, default="Noma'lum")
    dtc_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )
    raw_text = serializers.CharField(required=False, allow_blank=True, default="")