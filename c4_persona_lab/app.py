"""Launch PlotTwist locally or on a Gradio Hugging Face Space."""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).with_name('.env'))
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
from interface import create_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PlotTwist coursework app')
    parser.add_argument('--mode', choices=['auto','demo','live','local'], default=os.getenv('PLOTTWIST_MODE','auto'))
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', '7861')))
    parser.add_argument('--share', action='store_true', help='Create a temporary Gradio public URL')
    parser.add_argument('--host', default=os.getenv('GRADIO_SERVER_NAME','127.0.0.1'))
    args = parser.parse_args()
    demo = create_app(args.mode)
    demo.queue(default_concurrency_limit=4).launch(server_name=args.host, server_port=args.port, share=args.share, show_error=False)
