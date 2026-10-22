# -*- coding: utf-8 -*-
import json, sys
P = r"C:\Users\Administrator\.dsh\profiles\desktop\cordis.patch.yml"
text = open(P, "rb").read().decode("utf-8")
try:
    import yaml
    doc = yaml.safe_load(text)
    vr = [e for e in doc if isinstance(e, dict) and e.get("id") == "vision-router"]
    print("YAML PARSE: OK, entries=%d" % len(doc))
    print(json.dumps(vr[0], ensure_ascii=False, indent=2))
except ImportError:
    print("PYYAML 不可用，改用逐行核对")
    i = text.index("- id: vision-router")
    seg = text[i:i+1400]
    for n, ln in enumerate(seg.split("\n")[:24]):
        print("%3d | %s" % (n, ln))
except Exception as e:
    print("YAML PARSE FAILED:", type(e).__name__, e)
    i = text.index("- id: vision-router")
    print(repr(text[i:i+900]))
