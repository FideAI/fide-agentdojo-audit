"""Public derived projection; raw runs remain ignored. No source text or stack paths."""
import hashlib
OMIT={'command','commands','python','python_executable','guard_worker_sha256'}
def project(value):
    if isinstance(value,list):return [project(v) for v in value]
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            if k in OMIT or k=='stack':continue
            if k in ('prompt','goal'):
                out[k+'_sha256']=hashlib.sha256(v.encode()).hexdigest() if v is not None else None
            else:out[k]=project(v)
        return out
    return value
