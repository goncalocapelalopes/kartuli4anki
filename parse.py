from bs4 import BeautifulSoup
import pandas as pd
import requests

URL_BASE = "https://lingua.ge/verbs/"
TRNSLT_DIV_CLS = "elementor-text-editor elementor-clearfix"
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
	
	uid = "v" + verb_inf + tense
	result = [uid, verb_inf]

	url = URL_BASE + verb_inf
	series_idx, conj_offset  = CONJ_COORDS[tense]

	html = requests.get(url, headers=HEADERS).text
	soup = BeautifulSoup(html, "html.parser")
	try:
		# scope down to the section containing verb conjugations
		verbs_section = soup.find_all("div", class_=SECTION_WRP_CLS)[1]	
		
		# get the translated infinitive
		trnsltd_inf = verbs_section.find_all("div", class_=TRNSLT_DIV_CLS)[1].text
	
		# scope down further to the section containing the series of the tense
		tense_section = verbs_section.select(SECTION_TOP_CLS)[series_idx]
		
		# get the name of the tense
		tense_name = tense_section.find_all("span")[conj_offset].text

		# filter only the desired tense's conjugation
		conjs_div = tense_section.find_all("div", class_=TEXT_DIV_CLS)
	
		# 1 tense 6 conjugations
		conj_offset = conj_offset * 6
		conj = conjs_div[conj_offset:conj_offset+6]
	except:
		raise ValueError(f"Invalid verb infinitive {verb_inf}.")

	result.append(trnsltd_inf.strip())
	result.append(tense_name.strip())
	result.extend([c.text.strip() for c in conj])

	return result

def csvgen(verb_lst, df=None):
	cols = ["uid", "infinitive", "translation", "tense", "1s", "2s", "3s", "1p", "2p", "3p"]
	rows = []
	for verb in verb_lst:
		verb = verb.strip()
		for tense in CONJ_COORDS.keys():
			if df is not None:
				if "v" + verb + tense in df["uid"].tolist():
					print(f"Verb {verb} in tense {tense}  already in csv, skipping...")
					continue
			try:
				rows.append(get_conjugation(verb, tense))
			except Exception as e:
				print(e)
				break
	res = pd.DataFrame(columns=cols, data=rows)
	if df is not None:
		return pd.concat([df, res])
	else:
		return res 

if __name__ == "__main__":
	verbs = open("verbs.txt", "r").readlines()
	#prev_df = pd.read_csv("verbs.csv", index_col=False)
	csvgen(verbs).to_csv("verbs.csv", index=False)
