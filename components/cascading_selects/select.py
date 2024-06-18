from django_components import component

from a_predict.models import Department


@component.register("select_cascading_selects")
class SelectCascadingSelectsComponent(component.Component):
    template = """
        {% for model in models %}
            <option value="{{ model.id }}">{{ model.name }}</option>
        {% endfor %}
    """

    def get_context_data(self, unit, *args, **kwargs):
        models = Department.objects.filter(unit=unit).order_by("order")
        return {"models": models}

    def get(self, request, *args, **kwargs):
        unit = request.GET.get("unit")
        models = Department.objects.filter(unit=unit).order_by("order")
        return self.render_to_response({"models": models})
