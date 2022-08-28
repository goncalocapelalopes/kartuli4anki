from bs4 import BeautifulSoup
import requests

URL_BASE = "https://lingua.ge/verbs/"
SECTION_WRP_CLS = "elementor-section-wrap"
SECTION_TOP_CLS = "section.elementor-section.elementor-top-section"
TEXT_DIV_CLS = "elementor-text-editor elementor-clearfix"
CONJ_COORDS = {
	"PRESENT" : (2, 0),
	"IMPERFECT": (2, 1),
	"FUTURE": (3, 0),
	"AORIST": (4, 0),
	"OPTATIVE": (4, 1)
}
HEADERS = {"User-Agent": "XY"}

def get_conjugation(verb_inf, tense):
	if tense not in CONJ_COORDS.keys():
		raise ValueError("Invalid tense", tense, ".")

	url = URL_BASE + verb_inf
	series_idx, conj_offset  = CONJ_COORDS[tense]

	html = requests.get(url, headers=HEADERS).text
	soup = BeautifulSoup(html, "html.parser")
	
	# scope down to the section containing verb conjugations
	verbs_section = soup.find_all("div", class_=SECTION_WRP_CLS)[1]
	
	# scope down further to the section containing the series of the tense
	tense_section = verbs_section.select(SECTION_TOP_CLS)[series_idx]
	
	# filter only the desired tense's conjugation
	conjs_div = tense_section.find_all("div", class_=TEXT_DIV_CLS)
	
	# 1 tense 6 conjugations
	conj_offset = conj_offset * 6
	conj = conjs_div[conj_offset:conj_offset+6]
	return [c.text.strip() for c in conj]


if __name__ == "__main__":
	conj = get_conjugation("ჭამა", "OPTATIVE")
	print(conj)
