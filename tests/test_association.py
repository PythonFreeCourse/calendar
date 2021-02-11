import pytest


class TestAssociation:
    @pytest.mark.association
    def test_association_data(self, association, event):
        assert association.events == event

    @pytest.mark.association
    def test_repr(self, association):
        assert (
                association.__repr__()
                == f'<UserEvent ({association.participants}, '
                   f'{association.events})>')
