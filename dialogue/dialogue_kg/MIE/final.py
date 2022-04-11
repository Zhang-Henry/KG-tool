import argparse
import os
from dialogue.dialogue_kg.MIE.src import Dictionary, Ontology, Data, MIE, evaluate
from dialogue.dialogue_kg.MIE.src.eval import dialogue2window
# import tensorflow as tf



# parser = argparse.ArgumentParser(description='MIE')
# parser.add_argument('--add-global', type=bool, default=False, help='Add global module or not.')
# parser.add_argument('--hidden-size', type=int, default=400, help='Hidden size.')
# parser.add_argument('--mlp-layer-num', type=int, default=4, help='Number of layers of mlp.')
# parser.add_argument('--keep-p', type=float, default=0.8, help='1 - dropout rate.')
#
# parser.add_argument('--start-lr', type=float, default=1e-3, help='Start learning rate.')
# parser.add_argument('--end-lr', type=float, default=1e-4, help='End learning rate.')
# parser.add_argument('-e', '--epoch-num', type=int, default=100, help='Epoch num.')
# parser.add_argument('-b', '--batch-size', type=int, default=35, help='Batch size.')
# parser.add_argument('-t', '--tbatch-size', type=int, default=175, help='Test batch size.')
# parser.add_argument('-g', '--gpu-id', type=str, default='0', help='Gpu id.')
# parser.add_argument('-l', '--location', type=str, default='kgproject/dialogue_kg/MIE/model_files/MIE', help='Location to save.')
# args = parser.parse_args()
#

# params of the model.
# params = {
#     "add_global": args.add_global,
#     "num_units": args.hidden_size,
#     "num_layers": args.mlp_layer_num,
#     "keep_p": args.keep_p,
# }

# Test the model.
# pred_labels = evaluate(model, 'test', 100)
#
# print(pred_labels)