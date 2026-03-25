import ctypes, mmap, struct, numpy as np
from ._native import SparseBatch
from .config import DataloaderSkipConfig

MAGIC = b"BINPACK\x00"

class _PySparseStream:
    def __init__(self, feature_set_name, filenames, batch_size, cyclic, config: DataloaderSkipConfig):
        self.feat_n = None
        rows, targs = [], []
        for path in filenames:
            with open(path, "rb") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                if mm.read(8) != MAGIC: mm.close(); raise RuntimeError(f"{path}: bad magic")
                feat_n = struct.unpack("<i", mm.read(4))[0]
                count  = struct.unpack("<q", mm.read(8))[0]
                if self.feat_n is None: self.feat_n = feat_n
                elif self.feat_n != feat_n: mm.close(); raise RuntimeError("feature size mismatch")
                for _ in range(count):
                    vec = mm.read(feat_n); tgt = struct.unpack("<f", mm.read(4))[0]
                    rows.append(np.frombuffer(vec, dtype=np.uint8).copy()); targs.append(tgt)
                mm.close()
        if not rows: raise RuntimeError("No samples")
        self.rows   = np.stack(rows, axis=0)
        self.targets= np.asarray(targs, dtype=np.float32)
        self.N,self.F = self.rows.shape
        self.batch_size = int(batch_size); self.cyclic = bool(cyclic); self.pos = 0
        self.max_active = 1024
        self._keep = {}

    def _slice_to_sparse(self, s, e):
        sub = self.rows[s:e]; B = sub.shape[0]
        idxs, vals, max_act = [], [], 0
        for r in sub:
            nz = np.nonzero(r)[0]; 
            if nz.size > self.max_active: nz = nz[:self.max_active]
            idxs.append(nz.astype(np.int32)); vals.append(np.ones_like(nz, dtype=np.float32))
            if nz.size > max_act: max_act = nz.size
        max_act = max(1, max_act)
        wi = np.zeros((B,max_act), np.int32); bi = np.zeros((B,max_act), np.int32)
        wv = np.zeros((B,max_act), np.float32); bv = np.zeros((B,max_act), np.float32)
        for i,(nz,ones) in enumerate(zip(idxs,vals)):
            k = nz.size; wi[i,:k]=nz; bi[i,:k]=nz; wv[i,:k]=ones; bv[i,:k]=ones
        us = np.ones((B,1), np.float32); outc = np.zeros((B,1), np.float32)
        scor = self.targets[s:e].reshape(B,1)
        ps = np.zeros((B,), np.int32); ls = np.zeros((B,), np.int32)
        return wi,wv,bi,bv,us,outc,scor,ps,ls,max_act

    def fetch(self):
        if self.pos >= self.N:
            if not self.cyclic: return None
            self.pos = 0
        e = min(self.N, self.pos + self.batch_size)
        wi,wv,bi,bv,us,outc,scor,ps,ls,max_act = self._slice_to_sparse(self.pos, e); B = wi.shape[0]
        self._keep = {"wi":wi,"wv":wv,"bi":bi,"bv":bv,"us":us,"out":outc,"sc":scor,"ps":ps,"ls":ls}
        batch = SparseBatch()
        batch.num_inputs=self.F; batch.size=B
        batch.num_active_white_features=max_act; batch.num_active_black_features=max_act; batch.max_active_features=max_act
        batch.white=wi.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        batch.black=bi.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        batch.white_values=wv.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        batch.black_values=bv.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        batch.is_white=us.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        batch.outcome=outc.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        batch.score=scor.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        batch.psqt_indices=ps.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        batch.layer_stack_indices=ls.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        self.pos = e
        return ctypes.pointer(batch)

def create_sparse_batch_stream(feature_set, concurrency, filenames, batch_size, cyclic, config: DataloaderSkipConfig):
    return _PySparseStream(feature_set, filenames, batch_size, cyclic, config)

def destroy_sparse_batch_stream(stream): return

def fetch_next_sparse_batch(stream):
    ptr = stream.fetch()
    return ptr
