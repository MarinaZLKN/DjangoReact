from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


# creating the endpoints here
class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    # session_key is for the understanding if user is authenticated before sending the data
    def post(self, request, format=None):
        # so, if there is no key => session must be created
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # this will take all the data, serialize it and gives back the python representation of
        # it and the check if data was vaild
        serializer = self.serializer_class(data=request.data)
        # if data is vaild =>
        if serializer.is_valid():
            quest_can_pause = serializer.data.get('quest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            # define host by his session
            host = self.request.session.session_key
            # filter the rooms by host, if the host is already has created any rooms
            queryset = Room.objects.filter(host=host)
            # if yes,  updating the settings
            if queryset.exists():
                room = queryset[0]
                room.quest_can_pause = quest_can_pause
                room.votes_to_skip = votes_to_skip
                # updating the room and since we are updating, not creating => passing the fields we've updated
                room.save(update_fields=['quest_can_pause', 'votes_to_skip'])
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                # if creating
                room = Room(host=host, quest_can_pause=quest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
            # still need to return response weather it was valid or not
            # response must be serialized
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
