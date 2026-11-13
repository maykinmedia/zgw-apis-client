import base64
from datetime import date

import pytest

from tests.data import RSIN, create_catalogue, create_document_type
from zgw_apis_client import CatalogiClient, DocumentsClient
from zgw_apis_client.structs.catalogi import DocumentType
from zgw_apis_client.structs.documents import DocumentCreateData, DocumentListParams


@pytest.fixture
def document_type(catalogi_client: CatalogiClient) -> DocumentType:
    catalogue = create_catalogue(catalogi_client)
    return create_document_type(catalogi_client, catalogue)


def _document_data(document_type: DocumentType, *, titel: str) -> DocumentCreateData:
    return DocumentCreateData(
        bronorganisatie=RSIN,
        creatiedatum=date(2026, 2, 1),
        titel=titel,
        auteur="Test",
        taal="dut",
        informatieobjecttype=document_type.url,
        bestandsnaam=f"{titel}.txt",
        formaat="text/plain",
        inhoud=base64.b64encode(titel.encode()).decode(),
    )


@pytest.mark.vcr
def test_create_and_retrieve_document(
    documents_client: DocumentsClient, document_type: DocumentType
):
    document = documents_client.document.create(
        DocumentCreateData(
            bronorganisatie=RSIN,
            creatiedatum=date(2026, 2, 1),
            titel="Letter",
            auteur="Test",
            taal="dut",
            informatieobjecttype=document_type.url,
            bestandsnaam="letter.txt",
            formaat="text/plain",
            inhoud=base64.b64encode(b"Dear applicant").decode(),
            vertrouwelijkheidaanduiding="openbaar",
        )
    )

    assert document.titel == "Letter"
    assert document.versie == 1
    assert document.bestandsomvang == len(b"Dear applicant")
    assert not document.locked
    # on the way back, inhoud is a download URL
    assert document.inhoud is not None
    assert document.inhoud.startswith("http://")

    retrieved = documents_client.document.retrieve(document.url)
    assert retrieved == document


@pytest.mark.vcr
def test_list_documents(documents_client: DocumentsClient, document_type: DocumentType):
    first = documents_client.document.create(
        _document_data(document_type, titel="first")
    )
    second = documents_client.document.create(
        _document_data(document_type, titel="second")
    )

    page = documents_client.document.list()
    assert page.count == 2
    assert {document.url for document in page.results} == {first.url, second.url}

    page = documents_client.document.list(params=DocumentListParams(titel="second"))
    assert [document.url for document in page.results] == [second.url]
