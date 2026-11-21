import re
from collections.abc import Iterator

from .pola import pusty


def _sloty(obiekt, sciezka: str, droga: str = "") -> Iterator[tuple[dict, str, str]]:
    glowa, nawias, reszta = sciezka.partition("[]")
    klucze = [k for k in glowa.split(".") if k]
    if not nawias:
        *rodzice, ostatni = klucze
        for k in rodzice:
            obiekt = obiekt.get(k) if isinstance(obiekt, dict) else None
        if isinstance(obiekt, dict) and ostatni in obiekt:
            yield obiekt, ostatni, droga + glowa
        return
    for k in klucze:
        obiekt = obiekt.get(k) if isinstance(obiekt, dict) else None
    for i, element in enumerate(obiekt if isinstance(obiekt, list) else []):
        yield from _sloty(element, reszta, f"{droga}{glowa}[{i}]")


def _w_tekscie(wartosc, tekst: str) -> re.Match | None:
    s = str(wartosc)
    if s.isdigit():
        return re.search(r"(?<!\d)" + r"[\s-]?".join(s) + r"(?!\d)", tekst)
    return re.search(r"\s+".join(map(re.escape, s.split())), tekst)


def _kandydaci(dokumenty: list[dict], cel: dict, zrodla: dict) -> list[tuple[object, str]]:
    return [(rodzic[klucz], f"{typ_z} {sciezka_z}") for typ_z, sciezka_z in zrodla.items()
            for d in dokumenty if d is not cel and d["typ"] == typ_z
            for rodzic, klucz, _ in _sloty(d["dane"], sciezka_z) if rodzic[klucz] not in (None, "")]


def _dodaj_element(dane: dict, szablon: dict, sciezka: str) -> None:
    glowa = sciezka.partition("[]")[0]
    lista, wzor = dane, szablon
    for k in glowa.split("."):
        lista, wzor = lista[k], wzor[k]
    if not lista:
        lista.append(pusty(wzor[0]))


def uzupelnij_sprawe(dokumenty: list[dict], typy: dict[str, dict]) -> None:
    for cel in dokumenty:
        typ = typy.get(cel["typ"])
        for sciezka, zrodla in (typ or {}).get("kontekst", {}).items():
            obecni = [(w, skad, m) for w, skad in _kandydaci(dokumenty, cel, zrodla) if (m := _w_tekscie(w, cel["tekst"]))]
            if not obecni:
                continue
            if "[]" in sciezka:
                _dodaj_element(cel["dane"], typ["szablon"], sciezka)
            uzyte = {rodzic[klucz] for rodzic, klucz, _ in _sloty(cel["dane"], sciezka)}
            for rodzic, klucz, konkretna in _sloty(cel["dane"], sciezka):
                if rodzic[klucz] is not None:
                    continue
                wolny = next(((w, skad, m) for w, skad, m in obecni if w not in uzyte), None)
                if wolny is None:
                    break
                wartosc, skad, m = wolny
                rodzic[klucz] = wartosc
                uzyte.add(wartosc)
                cel["dziennik"].append({"pole": konkretna, "wartosc": wartosc, "regula": f"kontekst sprawy: {skad}",
                                        "fragment": " ".join(m[0].split())})
