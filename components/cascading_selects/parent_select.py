from typing import Any, Dict
from django_components import component
from django_components import types as t

from a_predict.models import Unit


@component.register("parent_select_cascading_selects")
class ParentSelectCascadingSelectsComponent(component.Component):
    template: t.django_html = """
        <div>
            <label class="label">Unit</label>
            <select class="input" name="unit" hx-get="{% url 'select_cascading_selects' %}" hx-target="#models">
            {% for obj in objects %}
                <option value="{{ obj.id }}">{{ obj.unit }}</option>
            {% endfor %}
            </select>
        </div>
        <div class="mt-2">
            <label class="label">Model</label>
            <select id="models" name="model" class="input">
                {% component "select_cascading_selects" unit=units.0.id %}{% endcomponent %}
            </select>
        </div>
    """

    def get_context_data(self, objects, *args, **kwargs) -> Dict[str, Any]:
        return {"objects": objects}
