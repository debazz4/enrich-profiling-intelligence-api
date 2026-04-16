from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import enrich_profile, ExternalAPIError


class ProfileListCreateView(APIView):

    def post(self, request):
        name = request.data.get("name")

        # name valkidation
        if name is None or name == "":
            return Response(
                {"status": "error", "message": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(name, str):
            return Response(
                {"status": "error", "message": "Invalid data type"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        name = name.lower()

        # idempotency check here
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return Response({
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileSerializer(existing).data
            })

        # enriching data
        try:
            data = enrich_profile(name)
        except ExternalAPIError as e:
            return Response(
                {
                    "status": "502",
                    "message": f"{e.api_name} returned an invalid response"
                },
                status=502
            )

        # save
        try:
            profile = Profile.objects.create(
                name=name,
                **data
            )
        except IntegrityError:
            # Fetch existing (idempotency fallback)
            existing = Profile.objects.filter(name=name).first()

            return Response({
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileSerializer(existing).data
            })

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        }, status=201)

    def get(self, request):
        queryset = Profile.objects.all()

        gender = request.GET.get("gender")
        country_id = request.GET.get("country_id")
        age_group = request.GET.get("age_group")

        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)

        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)

        serializer = ProfileListSerializer(queryset, many=True)

        return Response({
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data
        })

class ProfileDetailView(APIView):

    def get(self, request, id):
        """Get a single profile details with its id."""
        try:
            profile = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", 
                "message": "Profile not found"},
                status=404
            )

        return Response({
            "status": "success",
            "data": ProfileSerializer(profile).data
        })

    def delete(self, request, id):
        """Deletes a single profile from db with its id."""
        try:
            profile = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found"},
                status=404
            )

        profile.delete()
        return Response(status=204)