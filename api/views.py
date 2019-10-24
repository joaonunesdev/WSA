from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import render
from .bn import Node, WSA


def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')


class NPTView(APIView):
    """
    A view that can accept POST requests with JSON content.
    """    
    permission_classes = (permissions.IsAuthenticated,) 

    def post(self, request, format=None):
        try:
            parents = request.data['parents']
            title = request.data['title']
            states = request.data['states']
            compatible_parents = request.data['compatible_parents']

            child_node = Node(title, states)
            
            for parent in parents:
                parent_obj = Node(parent['title'], parent['states'])
                child_node.add_parent(parent_obj, parent['weight'])

            for cp in compatible_parents:
                child_node.npt.add_compatible(cp['configuration'], cp['dist'], cp['parent'])
            
            WSA.apply(child_node)
        
        except (Exception):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response({'npt': child_node.npt.to_list()})