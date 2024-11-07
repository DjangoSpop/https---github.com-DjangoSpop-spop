from rest_framework import serializers

from reports.models import Reports


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
      model =  Reports
      fields = '__all__'

