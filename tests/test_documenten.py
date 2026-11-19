import base64
from datetime import date

import pytest

from zgw_apis_client import CatalogiClient, DocumentenClient
from zgw_apis_client.structs.catalogi import InformatieObjectType
from zgw_apis_client.structs.documenten import (
    EnkelvoudigInformatieObjectCreateData,
    EnkelvoudigInformatieObjectListParams,
)

from .data import RSIN, create_catalogus, create_informatieobjecttype


@pytest.fixture
def informatieobjecttype(catalogi_client: CatalogiClient) -> InformatieObjectType:
    catalogus = create_catalogus(catalogi_client)
    return create_informatieobjecttype(catalogi_client, catalogus)


def _informatieobject_data(
    informatieobjecttype: InformatieObjectType, *, titel: str
) -> EnkelvoudigInformatieObjectCreateData:
    return EnkelvoudigInformatieObjectCreateData(
        bronorganisatie=RSIN,
        creatiedatum=date(2026, 2, 1),
        titel=titel,
        auteur="Test",
        taal="dut",
        informatieobjecttype=informatieobjecttype.url,
        bestandsnaam=f"{titel}.txt",
        formaat="text/plain",
        inhoud=base64.b64encode(titel.encode()).decode(),
    )


@pytest.mark.vcr
def test_create_and_retrieve_enkelvoudiginformatieobject(
    documenten_client: DocumentenClient, informatieobjecttype: InformatieObjectType
):
    enkelvoudiginformatieobject = documenten_client.enkelvoudiginformatieobject.create(
        data=EnkelvoudigInformatieObjectCreateData(
            bronorganisatie=RSIN,
            creatiedatum=date(2026, 2, 1),
            titel="Letter",
            auteur="Test",
            taal="dut",
            informatieobjecttype=informatieobjecttype.url,
            bestandsnaam="letter.txt",
            formaat="text/plain",
            inhoud=base64.b64encode(b"Dear applicant").decode(),
            vertrouwelijkheidaanduiding="openbaar",
        )
    )

    assert enkelvoudiginformatieobject.titel == "Letter"
    assert enkelvoudiginformatieobject.versie == 1
    assert enkelvoudiginformatieobject.bestandsomvang == len(b"Dear applicant")
    assert not enkelvoudiginformatieobject.locked
    # on the way back, inhoud is a download URL
    assert enkelvoudiginformatieobject.inhoud is not None
    assert enkelvoudiginformatieobject.inhoud.startswith("http://")

    retrieved = documenten_client.enkelvoudiginformatieobject.retrieve(
        identifier=enkelvoudiginformatieobject.url
    )
    assert retrieved == enkelvoudiginformatieobject


@pytest.mark.vcr
def test_list_enkelvoudiginformatieobjecten(
    documenten_client: DocumentenClient, informatieobjecttype: InformatieObjectType
):
    first = documenten_client.enkelvoudiginformatieobject.create(
        data=_informatieobject_data(informatieobjecttype, titel="first")
    )
    second = documenten_client.enkelvoudiginformatieobject.create(
        data=_informatieobject_data(informatieobjecttype, titel="second")
    )

    page = documenten_client.enkelvoudiginformatieobject.list()
    assert page.count == 2
    assert {
        enkelvoudiginformatieobject.url for enkelvoudiginformatieobject in page.results
    } == {first.url, second.url}

    page = documenten_client.enkelvoudiginformatieobject.list(
        params=EnkelvoudigInformatieObjectListParams(titel="second")
    )
    assert [
        enkelvoudiginformatieobject.url for enkelvoudiginformatieobject in page.results
    ] == [second.url]
