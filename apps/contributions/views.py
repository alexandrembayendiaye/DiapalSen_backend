from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Contribution
from .serializers import ContributionSerializer
from rest_framework.views import APIView


class ContributionCreateView(generics.CreateAPIView):
    """
    Vue pour permettre à un utilisateur connecté de contribuer à un projet.
    """

    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ProjectContributionsListView(generics.ListAPIView):
    """
    Liste les contributions associées à un projet spécifique.
    Accessible à tous (publique).
    """

    serializer_class = ContributionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        projet_id = self.kwargs.get("projet_id")
        return Contribution.objects.filter(projet_id=projet_id, statut="confirmee")


class UserContributionsListView(generics.ListAPIView):
    """
    Liste les contributions effectuées par l'utilisateur connecté.
    """

    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contribution.objects.filter(contributeur=self.request.user)


class ContributionConfirmView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        """
        Confirme une contribution (paiement validé)
        """
        try:
            contribution = Contribution.objects.get(pk=pk)
        except Contribution.DoesNotExist:
            return Response(
                {"detail": "Contribution introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if contribution.statut == "confirmee":
            return Response(
                {"detail": "Cette contribution est déjà confirmée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        contribution.statut = "confirmee"
        contribution.save()

        serializer = ContributionSerializer(contribution)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContributionDetailView(generics.RetrieveAPIView):
    """
    Permet à un utilisateur authentifié de voir les détails d'une contribution spécifique.
    - L'admin peut tout voir.
    - Un utilisateur normal ne peut voir que ses propres contributions.
    """

    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # admin
            return Contribution.objects.all()
        return Contribution.objects.filter(contributeur=user)
