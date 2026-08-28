from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalyzeDTCInputSerializer
from .services import get_ai_diagnostic_analysis


class AnalyzeDTCView(APIView):
    """
    Scanmatik OCR'dan kelgan DTC kodlarini tahlil qiluvchi API
    """

    def post(self, request):
        serializer = AnalyzeDTCInputSerializer(data=request.data)
        if serializer.is_valid():
            car_model = serializer.validated_data.get('car_model')
            dtc_codes = serializer.validated_data.get('dtc_codes')
            raw_text = serializer.validated_data.get('raw_text')

            # AI xizmatini chaqiramiz
            ai_response = get_ai_diagnostic_analysis(
                car_model=car_model,
                dtc_codes=dtc_codes,
                raw_text=raw_text
            )

            return Response(ai_response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)