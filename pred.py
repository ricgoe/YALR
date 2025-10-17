import cv2
import tempfile
from argparse import Namespace
from fairseq import checkpoint_utils, tasks, utils
from fairseq.dataclass.configs import GenerationConfig

class LipPredictor:
    def __init__(self, ckpt_path):
        modalities = ["video"]
        self.gen_subset = "test"
        self.gen_cfg = GenerationConfig(beam=20)
        self.models, self.saved_cfg, self.task = checkpoint_utils.load_model_ensemble_and_task([ckpt_path])
        self.models = [model.eval().cuda() for model in self.models]
        self.saved_cfg.task.modalities = modalities
    
    
    def make_dummy_set(self, video_path):
        vid = cv2.VideoCapture(video_path)
        num_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        data_dir = tempfile.mkdtemp()
        tsv_cont = ["/\n", f"test-0\t{video_path}\t{None}\t{num_frames}\t{int(16_000*num_frames/fps)}\n"]
        label_cont = ["DUMMY\n"]
        with open(f"{data_dir}/test.tsv", "w") as fo:
            fo.write("".join(tsv_cont))
        with open(f"{data_dir}/test.wrd", "w") as fo:
            fo.write("".join(label_cont))
        
        self.saved_cfg.task.data = data_dir
        self.saved_cfg.task.label_dir = data_dir
        return
    
    
    def predict(self, video_path, user_dir):
        self.make_dummy_set(video_path)
        
        # utils.import_user_module(Namespace(user_dir=user_dir))
        task = tasks.setup_task(self.saved_cfg.task)
        task.load_dataset(self.gen_subset, task_cfg=self.saved_cfg.task)
        generator = task.build_generator(self.models, self.gen_cfg)
        itr = task.get_batch_iterator(dataset=task.dataset(self.gen_subset)).next_epoch_itr(shuffle=False)
        sample = next(itr)
        sample = utils.move_to_cuda(sample)
        hypos = task.inference_step(generator, self.models, sample)
        ref = self.decode_fn(sample['target'][0].int().cpu(), task, generator)
        hypo = hypos[0][0]['tokens'].int().cpu()
        hypo = self.decode_fn(hypo, task, generator)
        return hypo
    
    def decode_fn(self, x, task, generator):
            dictionary = task.target_dictionary
            symbols_ignore = generator.symbols_to_strip_from_output
            symbols_ignore.add(dictionary.pad())
            return task.datasets[self.gen_subset].label_processors[0].decode(x, symbols_ignore)