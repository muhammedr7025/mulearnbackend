from rest_framework.views import APIView

from db.organization import College, OrgDiscordLink
from utils.permission import JWTUtils
from utils.response import CustomResponse
from .serializer import (
    CollegeCreateDeleteSerializer,
    CollegeListSerializer,
    CollegeEditSerializer,
)
from utils.utils import CommonUtils


class CollegeApi(APIView):
    def get(self, request, college_code=None):
        if college_code:
            colleges = College.objects.filter(id=college_code)
        else:
            colleges = College.objects.all().select_related(
                "created_by", "updated_by", "org", "lead"
            )

        paginated_queryset = CommonUtils.get_paginated_queryset(
            colleges,
            request,
            search_fields=["created_by__firstname"],
            sort_fields={"created_by": "created_by__firstname"},
        )
        serializer = CollegeListSerializer(
            paginated_queryset.get("queryset"), many=True
        )

        return CustomResponse().paginated_response(
            data=serializer.data, pagination=paginated_queryset.get("pagination")
        )

    def post(self, request):
        request_data = request.data
        request_data["created_by"] = request_data[
            "updated_by"
        ] = JWTUtils.fetch_user_id(request)

        serializer = CollegeCreateDeleteSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(serializer.data).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()


class CollegeUpdateDeleteApi(APIView):
    def delete(self, request, college_id):
        if college := College.objects.filter(id=college_id).first():
            college.delete()
            return CustomResponse(
                general_message="College succesfully deleted"
            ).get_success_response()
        return CustomResponse(general_message="Invalid college").get_failure_response()

    def patch(self, request, college_id):
        college = College.objects.filter(id=college_id).first()
        request_data = request.data
        request_data["updated_by"] = JWTUtils.fetch_user_id(request)
        if college is None:
            return CustomResponse(
                general_message="Invalid college"
            ).get_failure_response()
        serializer = CollegeEditSerializer(college, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(serializer.data).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()
