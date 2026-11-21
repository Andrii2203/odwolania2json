import json
import pytest

from odwolania2json.pipeline import przetworz, uzupelnij_sprawe, ustawienia, wczytaj_typy, wyciagnij
from tools.ocena_f1 import DANE, bez_prefiksu

pytestmark = pytest.mark.skipif(not DANE.exists(), reason="brak data/uzp — zob. AGENTS.md")


@pytest.mark.parametrize("sprawa", ["przyklad_17", "przyklad_42"])
def test_t3_przelew(sprawa):
    typ, dane = przetworz(DANE / sprawa / "potwierdzenie_przelewu.pdf", wczytaj_typy(), ustawienia())

    assert typ == "przelew"
    wzor = json.loads((DANE / sprawa / "przelew.json").read_text(encoding="utf-8"))
    assert bez_prefiksu(dane, ustawienia()) == bez_prefiksu(wzor, ustawienia())


@pytest.mark.parametrize("sprawa", ["przyklad_02", "przyklad_41", "przyklad_44"])
def test_t4_pelnomocnictwo(sprawa):
    typ, dane = przetworz(DANE / sprawa / "pelnomocnictwo.pdf", wczytaj_typy(), ustawienia())

    assert typ == "pelnomocnictwo"
    assert dane == json.loads((DANE / sprawa / "pelnomocnictwo.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sprawa", ["przyklad_01", "przyklad_03", "przyklad_41"])
def test_t6_odwolanie(sprawa):
    typ, dane = przetworz(DANE / sprawa / "odwolanie.pdf", wczytaj_typy(), ustawienia())

    assert typ == "odwolanie"
    assert dane == json.loads((DANE / sprawa / "odwolanie.json").read_text(encoding="utf-8"))


def test_t10_etykieta_nie_jest_wartoscia():
    typ = next(t for t in wczytaj_typy() if t["typ"] == "przelew")

    dane = wyciagnij("Data Opis Kwota\nData operacji 2026-04-09\nTytuł: opłata skarbowa od pełnomocnictwa\n", typ)

    assert dane["przelew_bankowy"]["tytul"] == "opłata skarbowa od pełnomocnictwa"


def test_t11_rachunek_z_pl():
    typ = next(t for t in wczytaj_typy() if t["typ"] == "przelew")

    dane = wyciagnij("Z rachunku: PL 62 2170 0008 9152 5017 5661 7062\nNa rachunek: 68 4382 2304 9992 2952 6283 4736\n", typ)

    assert (dane["przelew_bankowy"]["z_rachunku"], dane["przelew_bankowy"]["na_rachunek"]) == (
        "PL62217000089152501756617062", "68438223049992295262834736")


def test_t15_rachunek_iban():
    typ = next(t for t in wczytaj_typy() if t["typ"] == "przelew")

    dane = wyciagnij("Z rachunku: DE89 3704 0044 0532 0130 00 Kwota: 10,00 EUR\nNa rachunek: PL61 1090 1014 0000 0712 1981 2874\n", typ)

    assert (dane["przelew_bankowy"]["z_rachunku"], dane["przelew_bankowy"]["na_rachunek"]) == (
        "DE89370400440532013000", "PL61109010140000071219812874")


def test_t13_bramka_utnij():
    typ = next(t for t in wczytaj_typy() if t["typ"] == "odwolanie")
    dziennik = []

    dane = wyciagnij("Odwołujący:\nBelmoria Rozwiązania S.A. ul. Zaczarowana 78, 90-803 Łódź KRS: 9999405188, NIP: 9999284065\n",
                     typ, dziennik)

    assert dane["Odwolujacy"][0]["nazwa"] == "Belmoria Rozwiązania S.A."
    assert any("ucięte przed" in w["regula"] for w in dziennik if w["pole"] == "Odwolujacy[0].nazwa")


def test_t14_kontekst_sprawy():
    typy = {t["typ"]: t for t in wczytaj_typy()}
    tekst = "Pełnomocnictwo\nBelmoria Rozwiązania S.A., numer identyfikacji podatkowej 999-928-40-65, udziela pełnomocnictwa.\n"
    odwolanie = {"Odwolujacy": [{"nazwa": "Belmoria Rozwiązania S.A.", "nip": "9999284065", "krs": "9999405188"}]}
    dokumenty = [{"typ": "odwolanie", "tekst": "", "dane": odwolanie, "dziennik": []},
                 {"typ": "pelnomocnictwo", "tekst": tekst, "dane": wyciagnij(tekst, typy["pelnomocnictwo"]), "dziennik": []}]

    uzupelnij_sprawe(dokumenty, typy)

    mocodawca = dokumenty[-1]["dane"]["mocodawca"][0]["data"]
    assert (mocodawca["nip"], mocodawca["krs"]) == ("9999284065", None)
    assert any("kontekst sprawy" in w["regula"] for w in dokumenty[-1]["dziennik"])
