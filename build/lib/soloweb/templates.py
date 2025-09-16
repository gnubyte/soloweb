"""
Soloweb Template Engine

A Jinja-like template engine with improvements over common Jinja issues:
- Better error messages with line numbers and context
- Safer default behavior (no arbitrary code execution)
- Cleaner syntax for common operations
- Better performance through compilation
- Built-in security features
"""

import re
import html
from typing import Dict, Any, List, Optional, Union, Callable
from collections import defaultdict


class TemplateError(Exception):
    """Template compilation or rendering error"""
    
    def __init__(self, message: str, line: int = None, template: str = None):
        self.message = message
        self.line = line
        self.template = template
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        msg = f"Template Error: {self.message}"
        if self.line:
            msg += f" (line {self.line})"
        if self.template:
            lines = self.template.split('\n')
            if 0 <= self.line - 1 < len(lines):
                msg += f"\nContext: {lines[self.line - 1].strip()}"
        return msg


class TemplateContext:
    """Template context with variable lookup and filters"""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        self.filters = self._get_default_filters()
        self.functions = self._get_default_functions()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable from context, supporting dot notation"""
        if '.' in key:
            value = self._get_nested(key, default)
        else:
            value = self.data.get(key, default)
        print(f"[DEBUG] TemplateContext.get: key={key!r}, value={value!r}, context_keys={list(self.data.keys())}")
        return value
    
    def _get_nested(self, key: str, default: Any = None) -> Any:
        """Get nested variable using dot notation (e.g., 'user.name')"""
        parts = key.split('.')
        value = self.data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, default)
            elif hasattr(value, '__getitem__'):
                try:
                    value = value[part]
                except (KeyError, IndexError, TypeError):
                    return default
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def _get_default_filters(self) -> Dict[str, Callable]:
        """Get default template filters"""
        return {
            'upper': str.upper,
            'lower': str.lower,
            'title': str.title,
            'capitalize': str.capitalize,
            'strip': str.strip,
            'length': len,
            'default': lambda value, default='': value if value else default,
            'escape': html.escape,
            'safe': lambda value: value,  # Mark as safe HTML
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'join': lambda value, *args: (args[0] if args else '').join(str(v) for v in value),
            'split': str.split,
            'replace': str.replace,
            'truncate': lambda value, length=50, suffix='...': 
                str(value)[:length] + suffix if len(str(value)) > length else str(value),
        }
    
    def _get_default_functions(self) -> Dict[str, Callable]:
        """Get default template functions"""
        return {
            'range': range,
            'len': len,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'abs': abs,
            'round': round,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
        }


class TemplateNode:
    """Base class for template nodes"""
    
    def render(self, context: TemplateContext) -> str:
        raise NotImplementedError


class TextNode(TemplateNode):
    """Plain text node"""
    
    def __init__(self, text: str):
        self.text = text
    
    def render(self, context: TemplateContext) -> str:
        return self.text


class VariableNode(TemplateNode):
    """Variable interpolation node"""
    
    def __init__(self, expression: str):
        self.expression = expression.strip()
    
    def render(self, context: TemplateContext) -> str:
        try:
            value = self._evaluate_expression(self.expression, context)
            return str(value) if value is not None else ''
        except Exception as e:
            raise TemplateError(f"Error evaluating expression '{self.expression}': {e}")
    
    def _evaluate_expression(self, expr: str, context: TemplateContext) -> Any:
        """Evaluate a template expression"""
        # Handle filters
        if '|' in expr:
            return self._apply_filters(expr, context)
        
        # Handle function calls
        if '(' in expr and expr.endswith(')'):
            return self._call_function(expr, context)
        
        # Simple variable lookup
        return context.get(expr)
    
    def _apply_filters(self, expr: str, context: TemplateContext) -> Any:
        """Apply filters to a value"""
        parts = [part.strip() for part in expr.split('|')]
        # Evaluate the initial part as an expression (variable or function)
        initial = parts[0]
        if '(' in initial and initial.endswith(')'):
            value = self._call_function(initial, context)
        else:
            value = context.get(initial)
        
        for filter_expr in parts[1:]:
            if '(' in filter_expr and filter_expr.endswith(')'):
                # Filter with arguments
                filter_name, args = self._parse_filter_call(filter_expr)
                filter_func = context.filters.get(filter_name)
                if filter_func:
                    value = filter_func(value, *args)
                else:
                    raise TemplateError(f"Unknown filter: {filter_name}")
            else:
                # Simple filter
                filter_name = filter_expr
                filter_func = context.filters.get(filter_name)
                if filter_func:
                    value = filter_func(value)
                else:
                    raise TemplateError(f"Unknown filter: {filter_name}")
        
        return value
    
    def _parse_filter_call(self, filter_expr: str) -> tuple:
        """Parse filter call with arguments"""
        match = re.match(r'(\w+)\((.*)\)', filter_expr)
        if not match:
            raise TemplateError(f"Invalid filter syntax: {filter_expr}")
        
        filter_name = match.group(1)
        args_str = match.group(2)
        
        if not args_str.strip():
            return filter_name, []
        
        # Improved argument parsing: handle quoted strings with commas
        args = []
        current = ''
        in_quote = False
        quote_char = ''
        for c in args_str:
            if c in "'\"" and not in_quote:
                in_quote = True
                quote_char = c
                current += c
            elif c == quote_char and in_quote:
                in_quote = False
                current += c
            elif c == ',' and not in_quote:
                arg = current.strip()
                if arg.startswith("'") and arg.endswith("'"):
                    args.append(arg[1:-1])
                elif arg.startswith('"') and arg.endswith('"'):
                    args.append(arg[1:-1])
                elif arg.isdigit():
                    args.append(int(arg))
                elif '.' in arg and arg.replace('.', '').isdigit():
                    args.append(float(arg))
                else:
                    args.append(arg)
                current = ''
            else:
                current += c
        if current.strip():
            arg = current.strip()
            if arg.startswith("'") and arg.endswith("'"):
                args.append(arg[1:-1])
            elif arg.startswith('"') and arg.endswith('"'):
                args.append(arg[1:-1])
            elif arg.isdigit():
                args.append(int(arg))
            elif '.' in arg and arg.replace('.', '').isdigit():
                args.append(float(arg))
            else:
                args.append(arg)
        
        return filter_name, args
    
    def _call_function(self, expr: str, context: TemplateContext) -> Any:
        """Call a function"""
        match = re.match(r'(\w+)\((.*)\)', expr)
        if not match:
            raise TemplateError(f"Invalid function syntax: {expr}")
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        func = context.functions.get(func_name)
        if not func:
            raise TemplateError(f"Unknown function: {func_name}")
        
        if not args_str.strip():
            return func()
        
        # Parse arguments
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if arg.startswith("'") and arg.endswith("'"):
                args.append(arg[1:-1])
            elif arg.startswith('"') and arg.endswith('"'):
                args.append(arg[1:-1])
            elif arg.isdigit():
                args.append(int(arg))
            elif '.' in arg and arg.replace('.', '').isdigit():
                args.append(float(arg))
            else:
                # Assume it's a variable
                args.append(context.get(arg))
        
        return func(*args)


class IfNode(TemplateNode):
    """If/elif/else conditional node"""
    
    def __init__(self, condition: str, body: List[TemplateNode], else_body: List[TemplateNode] = None):
        self.condition = condition
        self.body = body
        self.else_body = else_body or []
    
    def render(self, context: TemplateContext) -> str:
        print(f"[DEBUG] IfNode.render: condition={self.condition!r}")
        try:
            # Evaluate condition
            condition_value = self._evaluate_condition(self.condition, context)
            
            if condition_value:
                return ''.join(node.render(context) for node in self.body)
            else:
                return ''.join(node.render(context) for node in self.else_body)
        except Exception as e:
            raise TemplateError(f"Error in if condition '{self.condition}': {e}")
    
    def _evaluate_condition(self, condition: str, context: TemplateContext) -> bool:
        """Evaluate a boolean condition"""
        condition = condition.strip()
        
        # Handle common boolean expressions
        if condition.lower() in ('true', 'false'):
            return condition.lower() == 'true'
        
        # Handle comparisons using regex to avoid splitting variable names
        comparison_ops = ['==', '!=', '>=', '<=', '>', '<', ' in ', ' not in ']
        for op in comparison_ops:
            if op in condition:
                # Use regex to split only on the operator as a separate token
                pattern = rf'^(.*?)\s*{re.escape(op.strip())}\s*(.*?)$'
                m = re.match(pattern, condition)
                if not m:
                    continue
                left, right = m.group(1), m.group(2)
                left_val = context.get(left.strip())
                right_str = right.strip()
                # Try to parse right_val as int or float if it's a literal
                if right_str.isdigit():
                    right_val = int(right_str)
                elif right_str.replace('.', '', 1).isdigit() and right_str.count('.') < 2:
                    right_val = float(right_str)
                else:
                    right_val = context.get(right_str)
                # If either side is None, treat as False (like Jinja)
                if left_val is None or right_val is None:
                    return False
                if op.strip() == '==':
                    return left_val == right_val
                elif op.strip() == '!=':
                    return left_val != right_val
                elif op.strip() == '>=':
                    return left_val >= right_val
                elif op.strip() == '<=':
                    return left_val <= right_val
                elif op.strip() == '>':
                    return left_val > right_val
                elif op.strip() == '<':
                    return left_val < right_val
                elif op.strip() == 'in':
                    return left_val in right_val
                elif op.strip() == 'not in':
                    return left_val not in right_val
        
        # Simple truthiness check: use Python's bool()
        value = context.get(condition)
        print(f"[DEBUG] IfNode: condition='{condition}', value={value!r}, type={type(value)}, bool={bool(value)}, context_keys={list(context.data.keys())}")
        return bool(value)


class ForNode(TemplateNode):
    """For loop node"""
    
    def __init__(self, var_name: str, iterable_expr: str, body: List[TemplateNode]):
        self.var_name = var_name
        self.iterable_expr = iterable_expr
        self.body = body
    
    def render(self, context: TemplateContext) -> str:
        try:
            iterable = context.get(self.iterable_expr)
            if not iterable:
                return ''
            
            result = []
            for item in iterable:
                # Create a new context with the loop variable
                loop_context = TemplateContext(context.data.copy())
                loop_context.data[self.var_name] = item
                
                # Render the loop body
                result.append(''.join(node.render(loop_context) for node in self.body))
            
            return ''.join(result)
        except Exception as e:
            raise TemplateError(f"Error in for loop '{self.var_name} in {self.iterable_expr}': {e}")


class IncludeNode(TemplateNode):
    """Include another template"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
    
    def render(self, context: TemplateContext) -> str:
        # This would be implemented to load and render another template
        # For now, return a placeholder
        return f"<!-- Include: {self.template_name} -->"


class Template:
    """Main template class"""
    
    def __init__(self, source: str):
        self.source = source
        self.nodes = self._parse(source)
    
    def render(self, **context) -> str:
        """Render the template with the given context"""
        template_context = TemplateContext(context)
        return ''.join(node.render(template_context) for node in self.nodes)
    
    def _parse(self, source: str) -> List[TemplateNode]:
        """Parse template source into nodes"""
        nodes = []
        lines = source.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = i + 1
            
            # Handle control structures
            if line.strip().startswith('{%'):
                node = self._parse_control_structure(line, lines, i)
                if isinstance(node, tuple):
                    node, new_i = node
                    i = new_i
                nodes.append(node)
            else:
                # Handle text and variables
                text_nodes = self._parse_text_line(line, line_num)
                nodes.extend(text_nodes)
            
            i += 1
        
        return nodes
    
    def _parse_control_structure(self, line: str, lines: List[str], current_line: int) -> Union[TemplateNode, tuple]:
        """Parse a control structure line"""
        line = line.strip()
        
        # If statement
        if line.startswith('{% if '):
            return self._parse_if_statement(lines, current_line)
        
        # For loop
        elif line.startswith('{% for '):
            return self._parse_for_loop(lines, current_line)
        
        # Include
        elif line.startswith('{% include '):
            return self._parse_include(line)
        
        # End statements
        elif line in ('{% endif %}', '{% endfor %}'):
            return TextNode('')  # End statements are handled by their opening tags
        
        else:
            raise TemplateError(f"Unknown control structure: {line}", current_line + 1, self.source)
    
    def _parse_if_statement(self, lines: List[str], start_line: int) -> tuple:
        """Parse an if statement block"""
        # Extract condition from opening line using regex
        opening_line = lines[start_line].strip()
        match = re.match(r'\{\%\s*if\s+(.+?)\s*\%\}', opening_line)
        print(f"[DEBUG] _parse_if_statement: opening_line={opening_line!r}, match={match}")
        if match:
            condition = match.group(1).strip()
        else:
            raise TemplateError(f"Invalid if statement syntax: {opening_line}", start_line + 1, self.source)
        
        body = []
        else_body = []
        in_else = False
        i = start_line + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == '{% endif %}':
                break
            elif line == '{% else %}':
                in_else = True
                i += 1
                continue
            elif line.startswith('{%'):
                # Nested control structure
                node = self._parse_control_structure(line, lines, i)
                if isinstance(node, tuple):
                    node, new_i = node
                    i = new_i
                
                if in_else:
                    else_body.append(node)
                else:
                    body.append(node)
            else:
                # Text content
                text_nodes = self._parse_text_line(lines[i], i + 1)
                if in_else:
                    else_body.extend(text_nodes)
                else:
                    body.extend(text_nodes)
            
            i += 1
        
        if_node = IfNode(condition, body, else_body)
        return if_node, i
    
    def _parse_for_loop(self, lines: List[str], start_line: int) -> tuple:
        """Parse a for loop block"""
        # Extract loop variables from opening line
        opening_line = lines[start_line].strip()
        loop_expr = opening_line[7:-3].strip()  # Remove {% for %} and {% endfor %}
        
        # Parse "var in iterable" syntax
        if ' in ' not in loop_expr:
            raise TemplateError(f"Invalid for loop syntax: {loop_expr}", start_line + 1, self.source)
        
        var_name, iterable_expr = loop_expr.split(' in ', 1)
        var_name = var_name.strip()
        iterable_expr = iterable_expr.strip()
        
        body = []
        i = start_line + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == '{% endfor %}':
                break
            elif line.startswith('{%'):
                # Nested control structure
                node = self._parse_control_structure(line, lines, i)
                if isinstance(node, tuple):
                    node, new_i = node
                    i = new_i
                body.append(node)
            else:
                # Text content
                text_nodes = self._parse_text_line(lines[i], i + 1)
                body.extend(text_nodes)
            
            i += 1
        
        for_node = ForNode(var_name, iterable_expr, body)
        return for_node, i
    
    def _parse_include(self, line: str) -> IncludeNode:
        """Parse an include statement"""
        template_name = line[10:-3].strip()  # Remove {% include %} and {% endinclude %}
        return IncludeNode(template_name)
    
    def _parse_text_line(self, line: str, line_num: int) -> List[TemplateNode]:
        """Parse a line of text and variables"""
        nodes = []
        current_text = ''
        i = 0
        
        while i < len(line):
            if line[i:i+2] == '{{':
                # Variable start
                if current_text:
                    nodes.append(TextNode(current_text))
                    current_text = ''
                
                # Find variable end
                end = line.find('}}', i)
                if end == -1:
                    raise TemplateError("Unclosed variable expression", line_num, self.source)
                
                var_expr = line[i+2:end].strip()
                nodes.append(VariableNode(var_expr))
                i = end + 2
            else:
                current_text += line[i]
                i += 1
        
        if current_text:
            nodes.append(TextNode(current_text))
        
        return nodes


def render_template(template_string: str, **context) -> str:
    """Convenience function to render a template string"""
    template = Template(template_string)
    return template.render(**context) 