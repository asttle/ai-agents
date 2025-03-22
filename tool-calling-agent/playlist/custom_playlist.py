import json
import os 
import base64
from smolagents import ToolCallingAgent, DuckDuckGoSearchTool, FinalAnswerTool, HfApiModel, Tool, tool, VisitWebpageTool
from opentelemetry.sdk.trace import TracerProvider

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

try:
    with open('../../config.json', 'r') as config_file:
        config = json.load(config_file)
        hf_token = config.get("HF_TOKEN", "")
        langfuse_public_key = config.get("LANGFUSE_PUBLIC_KEY", "")
        langfuse_secret_key = config.get("LANGFUSE_SECRET_KEY", "")
        if not hf_token:
            print("HF_TOKEN not found in config.json or is empty")
            exit(1)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)

LANGFUSE_AUTH=base64.b64encode(f"{langfuse_public_key}:{langfuse_secret_key}".encode()).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel" # EU data region
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://us.cloud.langfuse.com/api/public/otel" # US data region
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)
@tool
def suggest_workout_plan(body_part: str) -> str:
    """
    Suggests a workout plan based on the body part to be trained.
    Args:
        body_part: The part of the body to focus the workout on.
    """
    if body_part.lower() == "legs":
        return "4 sets of squats, 3 sets of lunges, 3 sets of leg press, 4 sets of leg extensions, 3 sets of calf raises."
    elif body_part.lower() == "chest":
        return "4 sets of bench press, 3 sets of incline dumbbell press, 3 sets of chest flyes, 3 sets of push-ups."
    elif body_part.lower() == "back":
        return "4 sets of pull-ups, 3 sets of rows, 3 sets of lat pulldowns, 3 sets of back extensions."
    elif body_part.lower() == "arms":
        return "4 sets of bicep curls, 3 sets of tricep extensions, 3 sets of hammer curls, 3 sets of dips."
    elif body_part.lower() == "shoulders":
        return "4 sets of overhead press, 3 sets of lateral raises, 3 sets of front raises, 3 sets of shrugs."
    elif body_part.lower() == "core":
        return "4 sets of crunches, 3 sets of planks, 3 sets of Russian twists, 3 sets of leg raises."
    else:
        return "Custom workout plan needed. Please search the web for specific exercises."

class WorkoutIntensityTool(Tool):
    name = "workout_intensity_recommender"
    description = """
    This tool suggests workout intensity and techniques based on experience level and goals.
    It returns customized workout advice."""
    
    inputs = {
        "experience_level": {
            "type": "string",
            "description": "The experience level (e.g., 'beginner', 'intermediate', 'advanced').",
        },
        "goal": {
            "type": "string",
            "description": "The fitness goal (e.g., 'strength', 'hypertrophy', 'endurance', 'weight loss').",
        }
    }
    
    output_type = "string"

    def forward(self, experience_level: str, goal: str):
        recommendations = {
            "beginner_strength": "Focus on proper form with moderate weights. Rest 2-3 minutes between sets. Aim for 3-5 reps at 75-85% of your 1RM.",
            "beginner_hypertrophy": "Use moderate weights with 8-12 reps per set. Rest 60-90 seconds between sets. Focus on mind-muscle connection.",
            "beginner_endurance": "Use lighter weights with 15-20 reps per set. Rest 30-60 seconds between sets. Focus on controlled movements.",
            "beginner_weight_loss": "Combine resistance training with cardio. Keep rest periods short (30-45 seconds) and focus on full-body movements.",
            
            "intermediate_strength": "Implement progressive overload with heavier weights. Rest 2-3 minutes between sets. Consider 5x5 or 3x3 protocols.",
            "intermediate_hypertrophy": "Incorporate drop sets and supersets. Vary rep ranges between 6-12. Rest 60-90 seconds between sets.",
            "intermediate_endurance": "Use circuit training with minimal rest. Aim for 12-15 reps per exercise and focus on controlled eccentric movements.",
            "intermediate_weight_loss": "Try HIIT workouts combined with compound exercises. Keep heart rate elevated and rest periods brief.",
            
            "advanced_strength": "Implement periodization techniques. Focus on compound movements with heavy weights (85-95% 1RM). Rest 3-5 minutes between sets.",
            "advanced_hypertrophy": "Use techniques like rest-pause, mechanical drop sets, and time under tension. Vary rep ranges and implement split routines.",
            "advanced_endurance": "Incorporate complexes and EMOM (Every Minute On the Minute) training. Focus on maintaining form during fatigue.",
            "advanced_weight_loss": "Use advanced interval techniques like Tabata or complex training. Combine resistance and metabolic conditioning."
        }
        
        key = f"{experience_level.lower()}_{goal.lower()}"
        return recommendations.get(key, "For your specific combination of experience and goals, consider consulting with a personal trainer for a customized approach.")

agent = ToolCallingAgent(
    tools=[
        DuckDuckGoSearchTool(), 
        VisitWebpageTool(),
        suggest_workout_plan,
        WorkoutIntensityTool()
    ], 
    model=HfApiModel(token=hf_token),
    max_steps=10,
    verbosity_level=2
)

agent.run("Its leg day. So suggest me workout plan and good spotify playlist")