import csv
import requests
import uuid
from django.db import IntegrityError
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Profile, User
from .serializers import ProfileSerializer, ProfileListSerializer
from .services import enrich_profile, ExternalAPIError
from .filters import apply_filters
from .sorting import apply_sorting
from .pagination import apply_pagination
from .nlp_parser import parse_query
from .permissions import IsAdmin, IsAnalyst
from rest_framework.views import APIView
from .throttles import BurstRateThrottle, SustainedRateThrottle, SearchRateThrottle, ExportRateThrottle

from .cookies import set_auth_cookies

from core.utils.pkce import generate_code_verifier, generate_code_challenge
from .validators import validate_query_params



class ProfileListCreateView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    throttle_classes = [BurstRateThrottle, SustainedRateThrottle]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnalyst()]
        return [IsAdmin()]

    def post(self, request):
        name = request.data.get("name")

        # name validation
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
        try:
            validate_query_params(request.GET)
        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid query parameters"},
                status=422
            )
        queryset = Profile.objects.all()

        # filtering
        queryset = apply_filters(queryset, request.GET)
        #sorting
        queryset = apply_sorting(queryset, request.GET) 

        # pagination
        try:
            data, total, page, limit = apply_pagination(queryset, request.GET)
        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid query parameters"},
                status=422
            )

        serializer = ProfileListSerializer(data, many=True)

        return Response({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": serializer.data
    })

class ProfileDetailView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    throttle_classes = [BurstRateThrottle]
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnalyst()]
        return [IsAdmin()]

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
    

class ProfileSearchView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAnalyst]

    throttle_classes = [SearchRateThrottle]

    """Handles query search"""
    def get(self, request):
        query = request.GET.get("q")

        if not query or query.strip() == "":
            return Response(
                {
                    "status": "error",
                    "message": "Invalid query parameters"
                },
                status=400
            )

        filters = parse_query(query)

        if not filters:
            return Response(
                {"status": "error", "message": "Unable to interpret query"},
                status=400
            )

        queryset = Profile.objects.all()
        queryset = apply_filters(queryset, filters)
        queryset = apply_sorting(queryset, request.GET)

        data, total, page, limit = apply_pagination(queryset, request.GET)

        serializer = ProfileListSerializer(data, many=True)

        return Response({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "data": serializer.data
        })
    
class ExportProfilesView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    throttle_classes = [ExportRateThrottle]
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="profiles.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "name",
            "age",
            "gender",
            "country_id",
            "country_name",
            "age_group",
            "gender_probability",
            "country_probability",
            "created_at"
        ])

        queryset = Profile.objects.all()

        for p in queryset:
            writer.writerow([
                p.name,
                p.age,
                p.gender,
                p.country_id,
                p.country_name,
                p.age_group,
                p.gender_probability,
                p.country_probability,
                p.created_at.isoformat()
            ])

        return response



class GitHubLoginCLIView(APIView):
    permission_classes = []

    def get(self, request):
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        state = f"cli_{uuid.uuid4()}"
        print(f"first-state: {state}")
        cache.set(f"pkce_verifier:{state}", verifier, timeout=300)

        url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
            f"&scope=read:user"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )

        return Response({
            "auth_url": url,
            "state": state
        })

            
class GitHubLoginView(APIView):
    permission_classes = []  # Public

    def get(self, request):
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        state = f"web_{uuid.uuid4()}"

        # Store verifier keyed by state (TTL: 10 minutes)
        #cache.set(f"pkce_verifier:{state}", verifier, timeout=600)
        cache.set(f"pkce_verifier:{state}", verifier, timeout=600)
        url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
            f"&scope=read:user"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )

        return redirect(url)

class GitHubCallbackView(APIView):
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        # -----------------------------
        # 1. Validate input
        # -----------------------------
        if not code or not state:
            return Response(
                {"status": "error", "message": "Invalid OAuth flow"},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_cli = state.startswith("cli_")
        # -----------------------------
        # 2. Retrieve PKCE verifier
        # -----------------------------
        cache_key = f"pkce_verifier:{state}"
        verifier = cache.get(cache_key)

        if not verifier:
            return Response(
                {"status": "error", "message": "Invalid or expired state"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # 3. Exchange code with GitHub
        # -----------------------------
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
                "code_verifier": verifier
            },
            timeout=10
        )

        

        token_data = token_response.json()

        # HARD FAILURE DEBUG
        if token_response.status_code != 200 or "error" in token_data:
            return Response(
                {
                    "status": "error",
                    "message": "GitHub token exchange failed",
                    "debug": token_data
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        access_token = token_data.get("access_token")

        if not access_token:
            return Response(
                {
                    "status": "error",
                    "message": "No access token returned by GitHub"
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # -----------------------------
        # 4. Fetch GitHub user
        # -----------------------------
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        

        user_data = user_response.json()

        if user_response.status_code != 200:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to fetch GitHub user",
                    "debug": user_data
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        username = user_data.get("login")
    

        if not username:
            return Response(
                {"status": "error", "message": "Invalid GitHub user"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # -----------------------------
        # 5. Create or get user
        # -----------------------------
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"role": "analyst"}
        )
        

        # 6. Generate JWT
        refresh = RefreshToken.for_user(user)

        # 7. Clean up PKCE state
        

        if is_cli:
            return redirect(
                f"http://127.0.0.1:8001/callback?code={code}&state={state}"
            )
        
        cache.delete(cache_key)
        response = redirect("http://127.0.0.1:5500/dashboard.html")

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return response


class WebLoginView(APIView):
    def post(self, request):
        user = request.user  # after OAuth login

        if not user:
            return Response({
                "status": "error",
                "message": "Unauthorized"
            }, status=401)

        response = JsonResponse({
            "status": "success"
        })

        return set_auth_cookies(response, user)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # requires blacklist app enabled

        except Exception:
            # Don't fail logout if token is invalid
            pass

        response = Response({
            "status": "success",
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

        # Delete cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    