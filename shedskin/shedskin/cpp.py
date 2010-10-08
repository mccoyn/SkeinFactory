'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

cpp.py: output C++ code

output equivalent C++ code, using templates and virtuals to support data and OO polymorphism.

class generateVisitor: inherits visitor pattern from compiler.visitor.ASTVisitor, to recursively generate C++ code for each syntactical Python construct. the constraint graph, with inferred types, is first 'merged' back to program dimensions (getgx().merged_inh).

'''

import textwrap, string
from distutils import sysconfig

from shared import *
import extmod

# --- code generation visitor; use type information
class generateVisitor(ASTVisitor):
    def __init__(self, module):
        self.output_base = os.path.join(getgx().output_dir, module.filename[:-3])
        self.out = file(self.output_base+'.cpp','w')
        self.indentation = ''
        self.consts = {}
        self.mergeinh = merged(getgx().types, inheritance=True)
        self.module = module
        self.name = module.ident
        self.filling_consts = False
        self.with_count = 0
        self.bool_wrapper = {}

    def insert_consts(self, declare): # XXX ugly
        if not self.consts: return
        self.filling_consts = True

        if declare: suffix = '.hpp'
        else: suffix = '.cpp'

        lines = file(self.output_base+suffix,'r').readlines()
        newlines = []
        j = -1
        for (i,line) in enumerate(lines):
            if line.startswith('namespace ') and not 'XXX' in line: # XXX
                j = i+1
            newlines.append(line)

            if i == j:
                pairs = []
                done = set()
                for (node, name) in self.consts.items():
                    if not name in done and node in self.mergeinh and self.mergeinh[node]: # XXX
                        ts = typesetreprnew(node, inode(node).parent)
                        if declare: ts = 'extern '+ts
                        pairs.append((ts, name))
                        done.add(name)

                newlines.extend(self.group_declarations(pairs))
                newlines.append('\n')

        newlines2 = []
        j = -1
        for (i,line) in enumerate(newlines):
            if line.startswith('void __init() {'):
                j = i
            newlines2.append(line)

            if i == j:
                todo = {}
                for (node, name) in self.consts.items():
                    if not name in todo:
                        todo[int(name[6:])] = node
                todolist = todo.keys()
                todolist.sort()
                for number in todolist:
                    if self.mergeinh[todo[number]]: # XXX
                        name = 'const_'+str(number)
                        self.start('    '+name+' = ')
                        self.visit(todo[number], inode(todo[number]).parent)
                        newlines2.append(self.line+';\n')

                newlines2.append('\n')

        file(self.output_base+suffix,'w').writelines(newlines2)
        self.filling_consts = False

    def insert_includes(self): # XXX ugly
        includes = get_includes(self.module)
        prop_includes = set(self.module.prop_includes) - set(includes)
        if not prop_includes: return

        lines = file(self.output_base+'.hpp','r').readlines()
        newlines = []

        prev = ''
        for line in lines:
            if prev.startswith('#include') and not line.strip():
                for include in prop_includes:
                    newlines.append('#include "%s"\n' % include)
            newlines.append(line)
            prev = line

        file(self.output_base+'.hpp','w').writelines(newlines)

    # --- group pairs of (type, name) declarations, while paying attention to '*'
    def group_declarations(self, pairs):
        group = {}
        for (type, name) in pairs:
            group.setdefault(type, []).append(name)

        result = []
        for (type, names) in group.items():
            names.sort()
            if type.endswith('*'):
                result.append(type+(', *'.join(names))+';\n')
            else:
                result.append(type+(', '.join(names))+';\n')

        return result

    def header_file(self):
        self.out = file(self.output_base+'.hpp','w')
        self.visit(self.module.ast, True)
        self.out.close()

    def classes(self, node):
        return set([t[0].ident for t in inode(node).types()])

    def output(self, text):
        print >>self.out, self.indentation+text

    def start(self, text=None):
        self.line = self.indentation
        if text: self.line += text
    def append(self, text):
        self.line += text
    def eol(self, text=None):
        if text: self.append(text)
        if self.line.strip():
            print >>self.out, self.line+';'

    def indent(self):
        self.indentation += 4*' '
    def deindent(self):
        self.indentation = self.indentation[:-4]

    def connector(self, node, func):
        if singletype(node, module): return '::'

        elif isinstance(func, function) and func.listcomp:
            return '->'
        elif isinstance(node, Name) and not lookupvar(node.name, func): # XXX
            return '::'

        return '->'

    def declaredefs(self, vars, declare): # XXX use group_declarations
        decl = {}
        for (name,var) in vars:
            if singletype(var, module) or var.invisible: # XXX buh
                continue
            typehu = typesetreprnew(var, var.parent)
            if not var.name in ['__exception', '__exception2']: # XXX
                decl.setdefault(typehu, []).append(self.cpp_name(name))
        decl2 = []
        for (t,names) in decl.items():
            names.sort()
            prefix=''
            if declare: prefix='extern '
            if t.endswith('*'):
                decl2.append(prefix+t+(', *'.join(names)))
            else:
                decl2.append(prefix+t+(', '.join(names)))
        return ';\n'.join(decl2)

    def get_constant(self, node):
        parent = inode(node).parent
        while isinstance(parent, function) and parent.listcomp: # XXX
            parent = parent.parent
        if isinstance(parent, function) and (parent.inherited or not self.inhcpa(parent)): # XXX
            return
        for other in self.consts: # XXX use mapping
            if node.value == other.value:
                return self.consts[other]
        self.consts[node] = 'const_'+str(len(self.consts))
        return self.consts[node]

    def module_hpp(self, node):
        define = '_'.join(self.module.mod_path).upper()+'_HPP'
        print >>self.out, '#ifndef __'+define
        print >>self.out, '#define __'+define+'\n'

        # --- include header files
        if self.module.dir == '': depth = 0
        else: depth = self.module.dir.count('/')+1

        includes = get_includes(self.module)
        if 'getopt.hpp' in includes: # XXX
            includes.add('os/__init__.hpp')
            includes.add('os/path.hpp')
            includes.add('stat.hpp')
        if 'os/__init__.hpp' in includes: # XXX
            includes.add('os/path.hpp')
            includes.add('stat.hpp')
        for include in includes:
            print >>self.out, '#include "'+include+'"'
        if includes: print >>self.out

        # --- namespaces
        print >>self.out, 'using namespace __shedskin__;'
        for n in self.module.mod_path:
            print >>self.out, 'namespace __'+n+'__ {'
        print >>self.out

        for child in node.node.getChildNodes():
            if isinstance(child, From) and child.modname != '__future__':
                mod_id = '__'+'__::__'.join(child.modname.split('.'))+'__'

                for (name, pseudonym) in child.names:
                    if name == '*':
                        for func in getgx().modules[child.modname].funcs.values():
                            if func.cp:
                                print >>self.out, 'using '+mod_id+'::'+self.cpp_name(func.ident)+';';
                        for cl in getgx().modules[child.modname].classes:
                            print >>self.out, 'using '+mod_id+'::'+cl+';';
                    else:
                        if not pseudonym: pseudonym = name
                        if not pseudonym in self.module.mv.globals:# or [t for t in self.module.mv.globals[pseudonym].types() if not isinstance(t[0], module)]:
                            print >>self.out, 'using '+mod_id+'::'+nokeywords(name)+';'
        print >>self.out

        # class declarations
        for child in node.node.getChildNodes():
            if isinstance(child, Class):
                cl = defclass(child.name)
                print >>self.out, 'class '+nokeywords(cl.ident)+';'
        print >>self.out

        # --- lambda typedefs
        self.func_pointers()

        # globals
        defs = self.declaredefs(list(getmv().globals.items()), declare=True);
        if defs:
            self.output(defs+';')
            print >>self.out

        # --- class definitions
        for child in node.node.getChildNodes():
            if isinstance(child, Class):
                self.class_hpp(child)

        # --- defaults
        if self.module.mv.defaults.items():
            for default, nr in self.module.mv.defaults.items():
                print >>self.out, 'extern '+typesetreprnew(default, None)+' '+('default_%d;'%nr)
            print >>self.out

        # function declarations
        if self.module != getgx().main_module:
            print >>self.out, 'void __init();'
        for child in node.node.getChildNodes():
            if isinstance(child, Function):
                func = getmv().funcs[child.name]
                if self.inhcpa(func):
                    self.visitFunction(func.node, declare=True)
        print >>self.out

        for n in self.module.mod_path:
            print >>self.out, '} // module namespace'

        if getgx().extension_module and self.module == getgx().main_module:
            extmod.convert_methods2(self, self.module.classes.values())

        print >>self.out, '#endif'

    def module_cpp(self, node):
        # --- external dependencies
        if self.module.filename.endswith('__init__.py'): # XXX nicer check
            print >>self.out, '#include "__init__.hpp"\n'
        else:
            print >>self.out, '#include "%s.hpp"\n' % self.module.ident

        # --- comments
        if node.doc:
            self.do_comment(node.doc)
            print >>self.out

        # --- namespace
        for n in self.module.mod_path:
            print >>self.out, 'namespace __'+n+'__ {'
        print >>self.out

        # --- globals
        defs = self.declaredefs(list(getmv().globals.items()), declare=False);
        if defs:
            self.output(defs+';')
            print >>self.out

        # --- defaults
        if self.module.mv.defaults.items():
            for default, nr in self.module.mv.defaults.items():
                print >>self.out, typesetreprnew(default, None)+' '+('default_%d;'%nr)
            print >>self.out

        # --- declarations
        self.listcomps = {}
        for (listcomp,lcfunc,func) in getmv().listcomps:
            self.listcomps[listcomp] = (lcfunc, func)
        self.do_listcomps(True)
        self.do_lambdas(True)
        print >>self.out

        # --- definitions
        self.do_listcomps(False)
        self.do_lambdas(False)
        for child in node.node.getChildNodes():
            if isinstance(child, Class):
                self.class_cpp(child)
            elif isinstance(child, Function):
                self.do_comments(child)
                self.visit(child)

        # --- __init
        self.output('void __init() {')
        self.indent()
        if self.module == getgx().main_module and not getgx().extension_module: self.output('__name__ = new str("__main__");\n')
        else: self.output('__name__ = new str("%s");\n' % self.module.ident)

        for child in node.node.getChildNodes():
            if isinstance(child, Function):
                for default in child.defaults:
                    if default in getmv().defaults:
                        self.start('')
                        self.visitm('default_%d = ' % getmv().defaults[default], default, ';')
                        self.eol()

            elif isinstance(child, Class):
                for child2 in child.code.getChildNodes():
                    if isinstance(child2, Function):
                        for default in child2.defaults:
                            if default in getmv().defaults:
                                self.start('')
                                self.visitm('default_%d = ' % getmv().defaults[default], default, ';')
                                self.eol()
                if child.name in getmv().classes:
                    cl = getmv().classes[child.name]
                    self.output('cl_'+cl.cpp_name+' = new class_("%s", %d, %d);' % (cl.cpp_name, cl.low, cl.high))
                    for varname in cl.parent.varorder:
                        var = cl.parent.vars[varname]
                        if var.initexpr:
                            self.start()
                            self.visitm(cl.ident+'::'+self.cpp_name(var.name)+' = ', var.initexpr, cl)
                            self.eol()

            elif isinstance(child, Discard):
                if isinstance(child.expr, Const) and child.expr.value == None: # XXX merge with visitStmt
                    continue
                if isinstance(child.expr, Const) and type(child.expr.value) == str:
                    continue

                self.start('')
                self.visit(child)
                self.eol()

            elif isinstance(child, From):
                mod_id = '__'+'__::__'.join(child.modname.split('.'))+'__'
                for (name, pseudonym) in child.names:
                    if name == '*':
                        for var in getgx().modules[child.modname].mv.globals.values():
                            if not var.invisible and not var.imported and not var.name.startswith('__') and var.types():
                                self.start(nokeywords(var.name)+' = '+mod_id+'::'+nokeywords(var.name))
                                self.eol()
                    else:
                        if not pseudonym: pseudonym = name
                        if pseudonym in self.module.mv.globals and not [t for t in self.module.mv.globals[pseudonym].types() if isinstance(t[0], module)]:
                            self.start(nokeywords(pseudonym)+' = '+mod_id+'::'+nokeywords(name))
                            self.eol()

            elif not isinstance(child, (Class, Function)):
                self.do_comments(child)
                self.visit(child)

        self.deindent()
        self.output('}\n')

        # --- close namespace
        for n in self.module.mod_path:
            print >>self.out, '} // module namespace'
        print >>self.out

        # --- c++ main/extension module setup
        if self.module == getgx().main_module:
            if getgx().extension_module:
                extmod.do_extmod(self)
            else:
                self.do_main()

    def visitModule(self, node, declare=False):
        if declare:
            self.module_hpp(node)
        else:
            self.module_cpp(node)

    def do_main(self):
        mods = getgx().modules.values()
        if [mod for mod in mods if mod.builtin and mod.ident == 'sys'] and not getgx().extension_module:
            print >>self.out, 'int main(int argc, char **argv) {'
        else:
            print >>self.out, 'int main(int, char **) {'
        self.do_init_modules()
        print >>self.out, '    __shedskin__::__start(__%s__::__init);' % self.module.ident
        print >>self.out, '}'

    def do_init_modules(self):
        mods = getgx().modules.values()
        mods.sort(key=lambda x: x.import_order)
        print >>self.out, '    __shedskin__::__init();'
        for mod in mods:
            if mod != getgx().main_module and mod.ident != 'builtin':
                if mod.ident == 'sys':
                    if getgx().extension_module:
                        print >>self.out, '    __sys__::__init(0, 0);'
                    else:
                        print >>self.out, '    __sys__::__init(argc, argv);'
                else:
                    print >>self.out, '    __'+'__::__'.join([n for n in mod.mod_path])+'__::__init();' # XXX sep func

    def do_comment(self, s):
        if not s: return
        doc = s.replace('/*', '//').replace('*/', '//').split('\n')
        self.output('/**')
        if doc[0].strip():
            self.output(doc[0])
        # re-indent the rest of the doc string
        rest = textwrap.dedent('\n'.join(doc[1:])).splitlines()
        for l in rest:
            self.output(l)
        self.output('*/')

    def do_comments(self, child):
        if child in getgx().comments:
            for n in getgx().comments[child]:
                self.do_comment(n)

    def visitContinue(self, node, func=None):
        self.start('continue')
        self.eol()

    def visitWith(self, node, func=None):
        self.start()
        if node.vars:
            self.visitm('WITH_VAR(', node.expr, ',', node.vars, func)
        else:
            self.visitm('WITH(', node.expr, func)
        self.append(',%d)' % self.with_count)
        self.with_count += 1
        print >>self.out, self.line
        self.indent()
        self.visit(node.body, func)
        self.deindent()
        self.output('END_WITH')

    def visitWhile(self, node, func=None):
        print >>self.out
        if node.else_:
            self.output('%s = 0;' % getmv().tempcount[node.else_])

        self.start('while (')
        self.bool_test(node.test, func)
        self.append(') {')
        print >>self.out, self.line
        self.indent()
        getgx().loopstack.append(node)
        self.visit(node.body, func)
        getgx().loopstack.pop()
        self.deindent()
        self.output('}')

        if node.else_:
            self.output('if (!%s) {' % getmv().tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def class_hpp(self, node, declare=True): # XXX remove declare
        cl = getmv().classes[node.name]
        self.output('extern class_ *cl_'+cl.cpp_name+';')

        # --- header
        pyobjbase = []
        if not cl.bases:
            pyobjbase = ['public pyobj']

        clnames = [namespaceclass(b) for b in cl.bases]
        self.output('class '+nokeywords(cl.ident)+' : '+', '.join(pyobjbase+['public '+clname for clname in clnames])+' {')

        self.do_comment(node.doc)
        self.output('public:')
        self.indent()

        self.class_variables(cl)

        # --- constructor
        need_init = False
        if '__init__' in cl.funcs:
            initfunc = cl.funcs['__init__']
            if self.inhcpa(initfunc):
                 need_init = True

        # --- default constructor
        if need_init:
            self.output(nokeywords(cl.ident)+'() {}')
        else:
            self.output(nokeywords(cl.ident)+'() { this->__class__ = cl_'+cl.cpp_name+'; }')

        # --- init constructor
        if need_init:
            self.func_header(initfunc, declare=True, is_init=True)
            self.indent()
            self.output('this->__class__ = cl_'+cl.cpp_name+';')
            self.output('__init__('+', '.join([self.cpp_name(f) for f in initfunc.formals[1:]])+');')
            self.deindent()
            self.output('}')

        # --- virtual methods
        if cl.virtuals:
            self.virtuals(cl, declare)

        # --- regular methods
        for func in cl.funcs.values():
            if func.node and not (func.ident=='__init__' and func.inherited):
                self.visitFunction(func.node, cl, declare)

        if cl.has_copy and not 'copy' in cl.funcs:
            self.copy_method(cl, '__copy__', declare)
        if cl.has_deepcopy and not 'deepcopy' in cl.funcs:
            self.copy_method(cl, '__deepcopy__', declare)

        if getgx().extension_module:
            extmod.convert_methods(self, cl, declare)

        self.deindent()
        self.output('};\n')

    def class_cpp(self, node, declare=False): # XXX declare
        cl = getmv().classes[node.name]

        if cl.virtuals:
            self.virtuals(cl, declare)

        if node in getgx().comments:
            self.do_comments(node)
        else:
            self.output('/**\nclass %s\n*/\n' % cl.ident)
        self.output('class_ *cl_'+cl.cpp_name+';\n')

        # --- method definitions
        for func in cl.funcs.values():
            if func.node and not (func.ident=='__init__' and func.inherited):
                self.visitFunction(func.node, cl, declare)
        if cl.has_copy and not 'copy' in cl.funcs:
            self.copy_method(cl, '__copy__', declare)
        if cl.has_deepcopy and not 'deepcopy' in cl.funcs:
            self.copy_method(cl, '__deepcopy__', declare)

        # --- class variable declarations
        if cl.parent.vars: # XXX merge with visitModule
            for var in cl.parent.vars.values():
                if var in getgx().merged_inh and getgx().merged_inh[var]:
                    self.start(typesetreprnew(var, cl.parent)+cl.ident+'::'+self.cpp_name(var.name))
                    self.eol()
            print >>self.out

    def class_variables(self, cl):
        # --- class variables
        if cl.parent.vars:
            for var in cl.parent.vars.values():
                if var in getgx().merged_inh and getgx().merged_inh[var]:
                    self.output('static '+typesetreprnew(var, cl.parent)+self.cpp_name(var.name)+';')
            print >>self.out

        # --- instance variables
        for var in cl.vars.values():
            if var.invisible: continue # var.name in cl.virtualvars: continue

            # var is masked by ancestor var
            vars = set()
            for ancestor in cl.ancestors():
                vars.update(ancestor.vars)
                #vars.update(ancestor.virtualvars)
            if var.name in vars:
                continue

            # virtual
            if var.name in cl.virtualvars:
                ident = var.name
                subclasses = cl.virtualvars[ident]

                merged = set()
                for m in [getgx().merged_inh[subcl.vars[ident]] for subcl in subclasses if ident in subcl.vars and subcl.vars[ident] in getgx().merged_inh]: # XXX
                    merged.update(m)

                ts = self.padme(typestrnew({(1,0): merged}, cl, True, cl))
                if merged:
                    self.output(ts+self.cpp_name(ident)+';')

            # non-virtual
            elif var in getgx().merged_inh and getgx().merged_inh[var]:
                self.output(typesetreprnew(var, cl)+self.cpp_name(var.name)+';')

        if [v for v in cl.vars if not v.startswith('__')]:
            print >>self.out

    def copy_method(self, cl, name, declare): # XXX merge?
        header = nokeywords(cl.ident)+' *'
        if not declare:
            header += nokeywords(cl.ident)+'::'
        header += name+'('
        self.start(header)

        if name == '__deepcopy__':
            self.append('dict<void *, pyobj *> *memo')
        self.append(')')

        if not declare:
            print >>self.out, self.line+' {'
            self.indent()
            self.output(nokeywords(cl.ident)+' *c = new '+nokeywords(cl.ident)+'();')
            if name == '__deepcopy__':
                self.output('memo->__setitem__(this, c);')

            for var in cl.vars.values():
                if var in getgx().merged_inh and getgx().merged_inh[var]:
                #if var not in cl.funcs and not var.invisible:
                    if name == '__deepcopy__':
                        self.output('c->%s = __deepcopy(%s);' % (var.name, var.name))
                    else:
                        self.output('c->%s = %s;' % (var.name, var.name))
            self.output('return c;')

            self.deindent()
            self.output('}\n')
        else:
            self.eol()

    def padme(self, x):
        if not x.endswith('*'): return x+' '
        return x

    def virtuals(self, cl, declare):
        for ident, subclasses in cl.virtuals.items():
            if not subclasses: continue

            # --- merge arg/return types
            formals = []
            retexpr = False

            for subcl in subclasses:
                if ident not in subcl.funcs: continue

                func = subcl.funcs[ident]
                sig_types = []

                if func.returnexpr:
                    retexpr = True
                    if func.retnode.thing in self.mergeinh:
                        sig_types.append(self.mergeinh[func.retnode.thing]) # XXX mult returns; some targets with return some without..
                    else:
                        sig_types.append(set()) # XXX

                for name in func.formals[1:]:
                    var = func.vars[name]
                    sig_types.append(self.mergeinh[var])
                formals.append(sig_types)

            merged = []
            for z in zip(*formals):
                merge = set()
                for types in z: merge.update(types)
                merged.append(merge)
                
            for subcl in subclasses:
                if ident in subcl.funcs:
                    formals = subcl.funcs[ident].formals[1:]
                    break
            ftypes = [self.padme(typestrnew({(1,0): m}, func.parent, True, func.parent)) for m in merged]

            # --- prepare for having to cast back arguments (virtual function call means multiple targets)
            for subcl in subclasses:
                if (ident in subcl.funcs):
                    subcl.funcs[ident].ftypes = ftypes
                else:
                    error('Function not found:  %s' % ident, None, warning = True)

            # --- virtual function declaration
            if declare:
                self.start('virtual ')
                if retexpr:
                    self.append(ftypes[0])
                    ftypes = ftypes[1:]
                else:
                    self.append('void ')
                self.append(self.cpp_name(ident)+'(')

                self.append(', '.join([t+f for (t,f) in zip(ftypes, formals)]))

                if ident in cl.funcs and self.inhcpa(cl.funcs[ident]):
                    self.eol(')')
                else:
                    if retexpr and self.mergeinh[func.retnode.thing] == set([(defclass('bool_'), 0)]):
                        self.eol(') { return False; }') # XXX msvc needs return statement
                    else:
                        self.eol(') { return 0; }') # XXX msvc needs return statement

                if ident in cl.funcs: cl.funcs[ident].declared = True

    def inhcpa(self, func):
        return hmcpa(func) or (func in getgx().inheritance_relations and [1 for f in getgx().inheritance_relations[func] if hmcpa(f)])

    def visitSlice(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            self.visit(inode(node.expr).fakefunc, func)
            self.eol()
        else:
            self.visit(inode(node.expr).fakefunc, func)

    def visitLambda(self, node, parent=None):
        self.append(getmv().lambdaname[node])

    def children_args(self, node, ts, func=None):
        if len(node.getChildNodes()):
            self.append(str(len(node.getChildNodes()))+', ')

        double = set(ts[ts.find('<')+1:-3].split(', ')) == set(['double']) # XXX whaa

        for child in node.getChildNodes():
            if double and self.mergeinh[child] == set([(defclass('int_'), 0)]):
                self.append('(double)(')

            if child in getmv().tempcount:
                self.append(getmv().tempcount[child])
            else:
                self.visit(child, func)

            if double and self.mergeinh[child] == set([(defclass('int_'), 0)]):
                self.append(')')

            if child != node.getChildNodes()[-1]:
                self.append(', ')
        self.append(')')

    def visitDict(self, node, func=None):
        self.append('(new '+typesetreprnew(node, func)[:-2]+'(')
        if node.items:
            self.append(str(len(node.items))+', ')
        for (key, value) in node.items:
            self.visitm('new tuple2'+typesetreprnew(node, func)[4:-2]+'(2,', key, ',', value, ')', func)
            if (key, value) != node.items[-1]:
                self.append(', ')
        self.append('))')

    def visittuplelist(self, node, func=None):
        if isinstance(func, class_): # XXX
            func=None
        ts = typesetreprnew(node, func)
        self.append('(new '+ts[:-2]+'(')
        self.children_args(node, ts, func)
        self.append(')')

    def visitTuple(self, node, func=None):
        self.visittuplelist(node, func)

    def visitList(self, node, func=None):
        self.visittuplelist(node, func)

    def visitAssert(self, node, func=None):
        self.start('ASSERT(')
        self.visitm(node.test, ', ', func)
        if len(node.getChildNodes()) > 1:
            self.visit(node.getChildNodes()[1], func)
        else:
            self.append('0')
        self.eol(')')

    def visitm(self, *args):
        if args and isinstance(args[-1], (function, class_)):
            func = args[-1]
        else:
            func = None

        for arg in args[:-1]:
            if not arg: return
            if isinstance(arg, str):
                self.append(arg)
            else:
                self.visit(arg, func)

    def visitRaise(self, node, func=None):
        cl = None # XXX sep func
        t = [t[0] for t in self.mergeinh[node.expr1]]
        if len(t) == 1:
            cl = t[0]

        self.start('throw (')
        # --- raise class [, constructor args]
        if isinstance(node.expr1, Name) and not lookupvar(node.expr1.name, func): # XXX lookupclass
            self.append('new %s(' % node.expr1.name)
            if node.expr2:
                if isinstance(node.expr2, Tuple) and node.expr2.nodes:
                    for n in node.expr2.nodes:
                        self.visit(n, func)
                        if n != node.expr2.nodes[-1]: self.append(', ') # XXX visitcomma(nodes)
                else:
                    self.visit(node.expr2, func)
            self.append(')')
        # --- raise instance
        elif isinstance(cl, class_) and cl.mv.module.ident == 'builtin' and not [a for a in cl.ancestors_upto(None) if a.ident == 'BaseException']:
            self.append('new Exception()')
        else:
            self.visit(node.expr1, func)
        self.eol(')')

    def visitTryExcept(self, node, func=None):
        # try
        self.start('try {')
        print >>self.out, self.line
        self.indent()
        if node.else_:
            self.output('%s = 0;' % getmv().tempcount[node.else_])
        self.visit(node.body, func)
        if node.else_:
            self.output('%s = 1;' % getmv().tempcount[node.else_])
        self.deindent()
        self.start('}')

        # except
        for handler in node.handlers:
            if isinstance(handler[0], Tuple):
                pairs = [(n, handler[1], handler[2]) for n in handler[0].nodes]
            else:
                pairs = [(handler[0], handler[1], handler[2])]

            for (h0, h1, h2) in pairs:
                if isinstance(h0, Name) and h0.name in ['int', 'float', 'str', 'class']:
                    continue # XXX lookupclass
                elif h0:
                    cl = lookupclass(h0, getmv())
                    if cl.mv.module.builtin and cl.ident in ['KeyboardInterrupt', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemExit']:
                        error("system '%s' is not caught" % cl.ident, h0, warning=True)
                    arg = namespaceclass(cl)+' *'
                else:
                    arg = 'Exception *'

                if h1:
                    arg += h1.name

                self.append(' catch (%s) {' % arg)
                print >>self.out, self.line

                self.indent()
                self.visit(h2, func)
                self.deindent()
                self.start('}')

        print >>self.out, self.line

        # else
        if node.else_:
            self.output('if(%s) { // else' % getmv().tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def fastfor(self, node, assname, neg, func=None):
        # --- for i in range(..) -> for( i=l, u=expr; i < u; i++ ) ..
        ivar, evar = getmv().tempcount[node.assign], getmv().tempcount[node.list]
        self.start('FAST_FOR%s('%neg+assname+',')

        if len(node.list.args) == 1:
            self.append('0,')
            if node.list.args[0] in getmv().tempcount: # XXX in visit?
                self.append(getmv().tempcount[node.list.args[0]])
            else:
                self.visit(node.list.args[0], func)
            self.append(',')
        else:
            if node.list.args[0] in getmv().tempcount: # XXX in visit?
                self.append(getmv().tempcount[node.list.args[0]])
            else:
                self.visit(node.list.args[0], func)
            self.append(',')
            if node.list.args[1] in getmv().tempcount: # XXX in visit?
                self.append(getmv().tempcount[node.list.args[1]])
            else:
                self.visit(node.list.args[1], func)
            self.append(',')

        if len(node.list.args) != 3:
            self.append('1')
        else:
            if node.list.args[2] in getmv().tempcount: # XXX in visit?
                self.append(getmv().tempcount[node.list.args[2]])
            else:
                self.visit(node.list.args[2], func)
        self.append(',%s,%s)' % (ivar[2:],evar[2:]))
        print >>self.out, self.line

    def fastenum(self, node):
        return is_enum(node) and self.only_classes(node.list.args[0], ('tuple', 'list'))

    def fastzip2(self, node):
        names = ('tuple', 'list')
        return is_zip2(node) and self.only_classes(node.list.args[0], names) and self.only_classes(node.list.args[1], names)

    def only_classes(self, node, names):
        classes = [defclass(name) for name in names]+[defclass('none')]
        return not [t for t in self.mergeinh[node] if t[0] not in classes]

    def visitFor(self, node, func=None):
        if isinstance(node.assign, AssName):
            assname = node.assign.name
        elif isinstance(node.assign, AssAttr):
            self.start('')
            self.visitAssAttr(node.assign, func)
            assname = self.line.strip() # XXX yuck
        else:
            assname = getmv().tempcount[node.assign]
        assname = self.cpp_name(assname)

        print >>self.out
        if node.else_:
            self.output('%s = 0;' % getmv().tempcount[node.else_])

        if fastfor(node):
            self.do_fastfor(node, node, None, assname, func, False)
        elif self.fastenum(node):
            self.do_fastenum(node, func, False)
            self.forbody(node, None, assname, func, True, False)
        elif self.fastzip2(node):
            self.do_fastzip2(node, func, False)
            self.forbody(node, None, assname, func, True, False)
        else:
            pref, tail = self.forin_preftail(node)
            self.start('FOR_IN%s(%s,' % (pref, assname))
            self.visit(node.list, func)
            print >>self.out, self.line+','+tail+')'
            self.forbody(node, None, assname, func, False, False)
        print >>self.out

    def do_fastzip2(self, node, func, genexpr):
        self.start('FOR_IN_ZIP(')
        left, right = node.assign.nodes
        self.do_fastzip2_one(left, func)
        self.do_fastzip2_one(right, func)
        self.visitm(node.list.args[0], ',', node.list.args[1], ',', func)
        tail1 = getmv().tempcount[(node,2)][2:]+','+getmv().tempcount[(node,3)][2:]+','
        tail2 = getmv().tempcount[(node.list)][2:]+','+getmv().tempcount[(node,4)][2:]
        print >>self.out, self.line+tail1+tail2+')'
        self.indent()
        if isinstance(left, (AssTuple, AssList)):
            self.tuple_assign(left, getmv().tempcount[left], func)
        if isinstance(right, (AssTuple, AssList)):
            self.tuple_assign(right, getmv().tempcount[right], func)

    def do_fastzip2_one(self, node, func):
        if isinstance(node, (AssTuple, AssList)):
            self.append(getmv().tempcount[node])
        else:
            self.visit(node, func)
        self.append(',')

    def do_fastenum(self, node, func, genexpr):
        self.start('FOR_IN_SEQ(')
        left, right = node.assign.nodes
        self.do_fastzip2_one(right, func)
        self.visit(node.list.args[0], func)
        tail = getmv().tempcount[(node,2)][2:]+','+getmv().tempcount[node.list][2:]
        print >>self.out, self.line+','+tail+')'
        self.indent()
        self.start()
        self.visitm(left, ' = '+getmv().tempcount[node.list], func)
        self.eol()
        if isinstance(right, (AssTuple, AssList)):
            self.tuple_assign(right, getmv().tempcount[right], func)

    def forin_preftail(self, node):
        pref = '_NEW'
        tail = getmv().tempcount[node][2:]+','+getmv().tempcount[node.list][2:]
        if self.only_classes(node.list, ('tuple2',)):
            pref = '_T2'
        else:
            tail += ','+getmv().tempcount[(node,5)][2:]
        return pref, tail

    def forbody(self, node, quals, iter, func, skip, genexpr):
        if quals != None:
            self.listcompfor_body(node, quals, iter, func, False, genexpr)
            return

        if not skip:
            self.indent()
            if isinstance(node.assign, (AssTuple, AssList)):
                self.tuple_assign(node.assign, getmv().tempcount[node.assign], func)

        getgx().loopstack.append(node)
        self.visit(node.body, func)
        getgx().loopstack.pop()
        self.deindent()
        self.output('END_FOR')

        if node.else_:
            self.output('if (!%s) {' % getmv().tempcount[node.else_])
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def func_pointers(self):
        for func in getmv().lambdas.values():
            argtypes = [typesetreprnew(func.vars[formal], func).rstrip() for formal in func.formals]
            if func.largs != None:
                argtypes = argtypes[:func.largs]
            rettype = typesetreprnew(func.retnode.thing,func)
            print >>self.out, 'typedef %s(*lambda%d)(' % (rettype, func.lambdanr) + ', '.join(argtypes)+');'
        print >>self.out

    # --- function/method header
    def func_header(self, func, declare, is_init=False):
        method = isinstance(func.parent, class_)
        if method:
            formals = [f for f in func.formals if f != 'self']
        else:
            formals = [f for f in func.formals]
        if func.largs != None:
            formals = formals[:func.largs]

        ident = func.ident
        self.start()

        # --- return expression
        header = ''
        if is_init:
            ident = nokeywords(func.parent.ident)
        elif func.ident in ['__hash__']:
            header += 'int '
        elif func.returnexpr:
            header += typesetreprnew(func.retnode.thing, func) # XXX mult
        else:
            header += 'void '
            ident = self.cpp_name(ident)

        ftypes = [typesetreprnew(func.vars[f], func) for f in formals]

        # if arguments type too precise (e.g. virtually called) cast them back
        oldftypes = ftypes
        if func.ftypes:
            ftypes = func.ftypes[1:]

        # --- method header
        if method and not declare:
            header += nokeywords(func.parent.ident)+'::'

        if is_init:
            header += ident
        else:
            header += self.cpp_name(ident)

        # --- cast arguments if necessary (explained above)
        casts = []
        if func.ftypes:
            for i in range(min(len(oldftypes), len(ftypes))): # XXX this is 'cast on specialize'.. how about generalization?
                if oldftypes[i] != ftypes[i]:
                    casts.append(oldftypes[i]+formals[i]+' = ('+oldftypes[i]+')__'+formals[i]+';')
                    if not declare:
                        formals[i] = '__'+formals[i]

        formals2 = formals[:]
        for (i,f) in enumerate(formals2): # XXX
            formals2[i] = self.cpp_name(f)

        formaldecs = [o+f for (o,f) in zip(ftypes, formals2)]

        if declare and isinstance(func.parent, class_) and func.ident in func.parent.staticmethods:
            header = 'static '+header

        if is_init and not formaldecs:
            formaldecs = ['int __ss_init']

        if func.ident.startswith('__lambda'): # XXX
            header = 'static inline ' + header

        # --- output
        self.append(header+'('+', '.join(formaldecs)+')')
        if is_init:
            print >>self.out, self.line+' {'
        elif declare:
            self.eol()
        else:
            print >>self.out, self.line+' {'
            self.indent()

            if not declare and func.doc:
                self.do_comment(func.doc)

            for cast in casts:
                self.output(cast)
            self.deindent()

    def cpp_name(self, name, func=None):
        if self.module == getgx().main_module and name == 'init'+self.module.ident: # conflict with extmod init
            return '_'+name
        if name in [cl.ident for cl in getgx().allclasses]:
            return '_'+name
        elif name+'_' in [cl.ident for cl in getgx().allclasses]:
            return '_'+name
        elif name in self.module.funcs and func and isinstance(func.parent, class_) and name in func.parent.funcs:
            return '__'+func.mv.module.ident+'__::'+name

        return nokeywords(name)

    def visitFunction(self, node, parent=None, declare=False):
        # locate right func instance
        if parent and isinstance(parent, class_):
            func = parent.funcs[node.name]
        elif node.name in getmv().funcs:
            func = getmv().funcs[node.name]
        else:
            func = getmv().lambdas[node.name]

        if func.invisible or (func.inherited and not func.ident == '__init__'):
            return
        if declare and func.declared: # XXX
            return

        # check whether function is called at all (possibly via inheritance)
        if not self.inhcpa(func):
            if func.ident in ['__iadd__', '__isub__', '__imul__']:
                return
            if func.lambdanr is None and not repr(node.code).startswith("Stmt([Raise(CallFunc(Name('NotImplementedError')"):
                error(repr(func)+' not called!', node, warning=True)
            if not (declare and func.parent and func.ident in func.parent.virtuals):
                return

        if func.isGenerator and not declare:
            for var in func.vars:
                if var == 'next':
                    error("variable name 'next' cannot be used in generator", node)
            self.generator_class(func)

        self.func_header(func, declare)
        if declare:
            return
        self.indent()

        if func.isGenerator:
            self.generator_body(func)
            return

        # --- local declarations
        pairs = []
        for (name, var) in func.vars.items():
            if not var.invisible and name not in func.formals:
                name = self.cpp_name(name)
                ts = typesetreprnew(var, func)
                pairs.append((ts, name))
        self.output(self.indentation.join(self.group_declarations(pairs)))

        # --- function body
        self.visit(node.code, func)
        if func.fakeret:
            self.visit(func.fakeret, func)

        # --- add Return(None) (sort of) if function doesn't already end with a Return
        if node.getChildNodes():
            lastnode = node.getChildNodes()[-1]
            if not func.ident == '__init__' and not func.fakeret and not isinstance(lastnode, Return) and not (isinstance(lastnode, Stmt) and isinstance(lastnode.nodes[-1], Return)): # XXX use Stmt in moduleVisitor
                if not [1 for t in self.mergeinh[func.retnode.thing] if isinstance(t[0], class_) and t[0].ident == 'bool_']:
                    self.output('return 0;')

        self.deindent()
        self.output('}\n')

    def generator_ident(self, func): # XXX merge?
        if func.parent:
            return func.parent.ident + '_' + func.ident
        return func.ident
    
    def generator_class(self, func):
        ident = self.generator_ident(func)
        self.output('class __gen_%s : public %s {' % (ident, typesetreprnew(func.retnode.thing, func)[:-2]))
        self.output('public:')
        self.indent()
        pairs = [(typesetreprnew(func.vars[f], func), self.cpp_name(f)) for f in func.vars]
        self.output(self.indentation.join(self.group_declarations(pairs)))
        self.output('int __last_yield;\n')

        args = []
        for f in func.formals:
            args.append(typesetreprnew(func.vars[f], func)+self.cpp_name(f))
        self.output(('__gen_%s(' % ident) + ','.join(args)+') {')
        self.indent()
        for f in func.formals:
            self.output('this->%s = %s;' % (self.cpp_name(f),self.cpp_name(f)))
        self.output('__last_yield = -1;')
        self.deindent()
        self.output('}\n')

        self.output('%s __get_next() {' % typesetreprnew(func.retnode.thing, func)[7:-3])
        self.indent()
        self.output('switch(__last_yield) {')
        self.indent()
        for (i,n) in enumerate(func.yieldNodes):
            self.output('case %d: goto __after_yield_%d;' % (i,i))
        self.output('default: break;')
        self.deindent()
        self.output('}')

        for child in func.node.code.getChildNodes():
            self.visit(child, func)
        self.output('__stop_iteration = true;')
        self.deindent()
        self.output('}\n')

        self.deindent()
        self.output('};\n')

    def generator_body(self, func):
        ident = self.generator_ident(func)
        if not (func.isGenerator and func.parent):
            formals = [self.cpp_name(f) for f in func.formals]
        else:
            formals = ['this'] + [self.cpp_name(f) for f in func.formals if f != 'self']
        self.output('return new __gen_%s(%s);\n' % (ident, ','.join(formals)))
        self.deindent()
        self.output('}\n')

    def visitYield(self, node, func):
        self.output('__last_yield = %d;' % func.yieldNodes.index(node))
        self.return_expr(node.value, func.yieldnode, func, yield_=True)
        self.output('__after_yield_%d:;' % func.yieldNodes.index(node))
        self.start()

    def visitNot(self, node, func=None):
        self.append('__NOT(')
        self.bool_test(node.expr, func)
        self.append(')')

    def visitBackquote(self, node, func=None):
        self.visitm('repr(', inode(node.expr).fakefunc.node.expr, ')', func)

    def zeropointernone(self, node):
        return [t for t in self.mergeinh[node] if t[0].ident == 'none']

    def visitIf(self, node, func=None):
        for test in node.tests:
            self.start()
            if test != node.tests[0]:
                self.append('else ')
            self.append('if (')
            self.bool_test(test[0], func)
            print >>self.out, self.line+') {'
            self.indent()
            self.visit(test[1], func)
            self.deindent()
            self.output('}')

        if node.else_:
            self.output('else {')
            self.indent()
            self.visit(node.else_, func)
            self.deindent()
            self.output('}')

    def visitIfExp(self, node, func=None):
        self.append('((')
        self.bool_test(node.test, func)
        self.visitm(')?(', node.then, '):(', node.else_, '))', func)

    def visitBreak(self, node, func=None):
        if getgx().loopstack[-1].else_ in getmv().tempcount:
            self.output('%s = 1;' % getmv().tempcount[getgx().loopstack[-1].else_])
        self.output('break;')

    def visitStmt(self, node, func=None):
        for b in node.nodes:
            if isinstance(b, Discard):
                if isinstance(b.expr, Const) and b.expr.value == None:
                    continue
                if isinstance(b.expr, Const) and type(b.expr.value) == str:
                    self.do_comment(b.expr.value)
                    continue
                self.start('')
                self.visit(b, func)
                self.eol()
            else:
                self.visit(b, func)

    def visitOr(self, node, func=None):
        self.visitandor(node, node.nodes, '__OR', 'or', func)

    def visitAnd(self, node, func=None):
        self.visitandor(node, node.nodes,  '__AND', 'and', func)

    def visitandor(self, node, nodes, op, mix, func=None):
        if node in getgx().bool_test_only:
            self.append('(')
            for n in nodes:
                self.bool_test(n, func)
                if n != node.nodes[-1]:
                    self.append(' '+mix+' ')
            self.append(')')
        else:
            child = nodes[0]
            if len(nodes) > 1:
                self.append(op+'(')
            cast = ''
            if assign_needs_cast(child, func, node, func):
                cast = '(('+typesetreprnew(node, func)+')'
                self.append(cast)
            self.visit(child, func)
            if cast:
                self.append(')')
            if len(nodes) > 1:
                self.append(', ')
                self.visitandor(node, nodes[1:], op, mix, func)
                self.append(', '+getmv().tempcount[child][2:]+')')

    def visitCompare(self, node, func=None, wrapper=True):
        if not node in self.bool_wrapper:
            self.append('___bool(')
        self.done = set() # (tvar=fun())

        left = node.expr
        for op, right in node.ops:
            if op == '>': msg, short, pre = '__gt__', '>', None # XXX map = {}!
            elif op == '<': msg, short, pre = '__lt__', '<', None
            elif op == 'in': msg, short, pre = '__contains__', None, None
            elif op == 'not in': msg, short, pre = '__contains__', None, '!'
            elif op == '!=': msg, short, pre = '__ne__', '!=', None
            elif op == '==': msg, short, pre = '__eq__', '==', None
            elif op == 'is': msg, short, pre = None, '==', None
            elif op == 'is not': msg, short, pre = None, '!=', None
            elif op == '<=': msg, short, pre = '__le__', '<=', None
            elif op == '>=': msg, short, pre = '__ge__', '>=', None

            if msg == '__contains__':
                self.visitBinary(right, left, msg, short, func, pre)
            else:
                self.visitBinary(left, right, msg, short, func, pre)

            if right != node.ops[-1][1]:
                self.append('&&')
            left = right

        if not node in self.bool_wrapper:
            self.append(')')

    def visitAugAssign(self, node, func=None):
        if isinstance(node.node, Subscript):
            self.start()
            if set([t[0].ident for t in self.mergeinh[node.node.expr] if isinstance(t[0], class_)]) in [set(['dict']), set(['defaultdict'])] and node.op == '+=':
                self.visitm(node.node.expr, '->__addtoitem__(', inode(node).subs, ', ', node.expr, ')', func)
                self.eol()
                return

            self.visitm(inode(node).temp1+' = ', node.node.expr, func)
            self.eol()
            self.start()
            self.visitm(inode(node).temp2+' = ', inode(node).subs, func)
            self.eol()
        self.visit(inode(node).assignhop, func)

    def visitAdd(self, node, func=None):
        str_nodes = self.rec_string_addition(node)
        if str_nodes and len(str_nodes) > 2:
            self.append('__add_strs(%d, ' % len(str_nodes))
            for (i, node) in enumerate(str_nodes):
                self.visit(node, func)
                if i < len(str_nodes)-1:
                    self.append(', ')
            self.append(')')
        else:
            self.visitBinary(node.left, node.right, augmsg(node, 'add'), '+', func)

    def rec_string_addition(self, node):
        if isinstance(node, Add):
            l, r = self.rec_string_addition(node.left), self.rec_string_addition(node.right)
            if l and r:
                return l+r
        elif self.mergeinh[node] == set([(defclass('str_'),0)]):
            return [node]

    def visitBitand(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'and'), '&', func)

    def visitBitor(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'or'), '|', func)

    def visitBitxor(self, node, func=None):
        self.visitBitop(node, augmsg(node, 'xor'), '^', func)

    def visitBitop(self, node, msg, inline, func=None):
        self.visitBitpair(Bitpair(node.nodes, msg, inline), func)

    def visitBitpair(self, node, func=None):
        if len(node.nodes) == 1:
            self.visit(node.nodes[0], func)
        else:
            self.visitBinary(node.nodes[0], Bitpair(node.nodes[1:], node.msg, node.inline), node.msg, node.inline, func)

    def visitRightShift(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'rshift'), '>>', func)

    def visitLeftShift(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'lshift'), '<<', func)

    def visitMul(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'mul'), '*', func)

    def visitDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'div'), '/', func)

    def visitInvert(self, node, func=None): # XXX visitUnarySub merge, template function __invert?
        if unboxable(self.mergeinh[node.expr]):
            self.visitm('~', node.expr, func)
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)

    def visitFloorDiv(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'floordiv'), '//', func)

    def visitPower(self, node, func=None):
        self.power(node.left, node.right, None, func)

    def power(self, left, right, mod, func=None):
        inttype = set([(defclass('int_'),0)]) # XXX merge
        if self.mergeinh[left] == inttype and self.mergeinh[right] == inttype:
            if not isinstance(right, Const):
                error("pow(int, int) returns int after compilation", left, warning=True)

        if mod: self.visitm('__power(', left, ', ', right, ', ', mod, ')', func)
        else:
            if self.mergeinh[left].intersection(set([(defclass('int_'),0),(defclass('float_'),0)])) and isinstance(right, Const) and type(right.value) == int and right.value in [2,3]:
                self.visitm(('__power%d(' % int(right.value)), left, ')', func)
            else:
                self.visitm('__power(', left, ', ', right, ')', func)

    def visitSub(self, node, func=None):
        self.visitBinary(node.left, node.right, augmsg(node, 'sub'), '-', func)

    def par(self, node, thingy):
        if (isinstance(node, Const) and not isinstance(node.value, (int, float))) or not isinstance(node, (Name, Const)):
            return thingy
        return ''

    def visitBinary(self, left, right, middle, inline, func=None, prefix=''): # XXX cleanup please
        ltypes = self.mergeinh[left]
        origright = right
        if isinstance(right, Bitpair):
            right = right.nodes[0]
        rtypes = self.mergeinh[right]
        ul, ur = unboxable(ltypes), unboxable(rtypes)

        inttype = set([(defclass('int_'),0)]) # XXX new type?
        floattype = set([(defclass('float_'),0)]) # XXX new type?

        # --- inline mod/div
        if (floattype.intersection(ltypes) or inttype.intersection(ltypes)):
            if inline in ['%'] or (inline in ['/'] and not (floattype.intersection(ltypes) or floattype.intersection(rtypes))):
                if not defclass('complex') in [t[0] for t in rtypes]: # XXX
                    self.append({'%': '__mods', '/': '__divs'}[inline]+'(')
                    self.visit2(left, func)
                    self.append(', ')
                    self.visit2(origright, func)
                    self.append(')')
                    return

        # --- inline floordiv # XXX merge above?
        if (inline and ul and ur) and inline in ['//']:
            self.append({'//': '__floordiv'}[inline]+'(')
            self.visit2(left, func)
            self.append(',')
            self.visit2(right, func)
            self.append(')')
            return

        # --- inline other
        if inline and ((ul and ur) or not middle or (isinstance(left, Name) and left.name == 'None') or (isinstance(origright, Name) and origright.name == 'None')): # XXX not middle, cleanup?
            self.append('(')
            self.visit2(left, func)
            self.append(inline)
            self.visit2(origright, func)
            self.append(')')
            return

        # --- prefix '!'
        postfix = ''
        if prefix:
            self.append('('+prefix)
            postfix = ')'

        # --- comparison
        if middle in ['__eq__', '__ne__', '__gt__', '__ge__', '__lt__', '__le__']:
            self.append(middle[:-2]+'(')
            self.visit2(left, func)
            self.append(', ')
            if typesetreprnew(left, func) != typesetreprnew(origright, func):
                self.append('((%s)(' % typesetreprnew(left, func))
                self.visit2(origright, func)
                self.append('))')
            else:
                self.visit2(origright, func)
            self.append(')'+postfix)
            return

        # --- 1 +- ..j
        if inline in ['+', '-'] and isinstance(origright, Const) and isinstance(origright.value, complex):
            if floattype.intersection(ltypes) or inttype.intersection(ltypes):
                self.append('(new complex(')
                self.visit2(left, func)
                self.append(', '+{'+':'', '-':'-'}[inline]+str(origright.value.imag)+'))')
                return

        # --- 'a.__mul__(b)': use template to call to b.__mul__(a), while maintaining evaluation order
        if inline in ['+', '*', '-', '/'] and ul and not ur:
            self.append('__'+{'+':'add', '*':'mul', '-':'sub', '/':'div'}[inline]+'2(')
            self.visit2(left, func)
            self.append(', ')
            self.visit2(origright, func)
            self.append(')'+postfix)
            return

        # --- default: left, connector, middle, right
        self.append(self.par(left, '('))
        self.visit2(left, func)
        self.append(self.par(left, ')'))
        if middle == '==':
            self.append('==(')
        else:
            self.append(self.connector(left, func)+middle+'(')
        self.refer(origright, func, visit2=True) # XXX bleh
        self.append(')'+postfix)

    def visit2(self, node, func): # XXX use temp vars in comparisons, e.g. (t1=fun())
        if node in getmv().tempcount:
            if node in self.done:
                self.append(getmv().tempcount[node])
            else:
                self.visitm('('+getmv().tempcount[node]+'=', node, ')', func)
                self.done.add(node)
        else:
            self.visit(node, func)

    def visitUnarySub(self, node, func=None):
        self.visitm('(', func)
        if unboxable(self.mergeinh[node.expr]):
            self.visitm('-', node.expr, func)
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)
        self.visitm(')', func)

    def visitUnaryAdd(self, node, func=None):
        self.visitm('(', func)
        if unboxable(self.mergeinh[node.expr]):
            self.visitm('+', node.expr, func)
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)
        self.visitm(')', func)

    def refer(self, node, func, visit2=False):
        if isinstance(node, str):
            var = lookupvar(node, func)
            return node

        if isinstance(node, Name) and not node.name in ['None','True','False']:
            var = lookupvar(node.name, func)
        if visit2:
            self.visit2(node, func)
        else:
            self.visit(node, func)

    def library_func(self, funcs, modname, clname, funcname):
        for func in funcs:
            if not func.mv.module.builtin or func.mv.module.ident != modname:
                continue
            if clname != None:
                if not func.parent or func.parent.ident != clname:
                    continue
            return func.ident == funcname

    def add_args_arg(self, node, funcs):
        ''' append argument that describes which formals are actually filled in '''
        if self.library_func(funcs, 'datetime', 'time', 'replace') or \
           self.library_func(funcs, 'datetime', 'datetime', 'replace'):

            formals = funcs[0].formals[1:] # skip self
            formal_pos = dict([(v,k) for k,v in enumerate(formals)])
            positions = []

            for i, arg in enumerate(node.args):
                if isinstance(arg, Keyword):
                    positions.append(formal_pos[arg.name])
                else:
                    positions.append(i)

            if positions:
                self.append(str(reduce(lambda a,b: a|b, [(1<<x) for x in positions]))+', ')
            else:
                self.append('0, ')

    def visitCallFunc(self, node, func=None):
        objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(node)
        funcs = callfunc_targets(node, self.mergeinh)

        if self.library_func(funcs, 're', None, 'findall') or \
           self.library_func(funcs, 're', 're_object', 'findall'):
            error("'findall' does not work with groups (use 'finditer' instead)", node, warning=True)
        if self.library_func(funcs, 'socket', 'socket', 'settimeout') or \
           self.library_func(funcs, 'socket', 'socket', 'gettimeout'):
            error("socket.set/gettimeout do not accept/return None", node, warning=True)
        if self.library_func(funcs, 'builtin', None, 'map') and len(node.args) > 2:
            error("default fillvalue for 'map' becomes 0 for integers", node, warning=True)
        if self.library_func(funcs, 'itertools', None, 'izip_longest'):
            error("default fillvalue for 'izip_longest' becomes 0 for integers", node, warning=True)

        nrargs = len(node.args)
        if isinstance(func, function) and func.largs:
            nrargs = func.largs

        # --- target expression
        if node.node in self.mergeinh and [t for t in self.mergeinh[node.node] if isinstance(t[0], function)]: # anonymous function
            self.visitm(node.node, '(', func)

        elif constructor:
            self.append('(new '+nokeywords(typesetreprnew(node, func)[:-2])+'(')
            if funcs and len(funcs[0].formals) == 1 and not funcs[0].mv.module.builtin:
                self.append('1') # don't call default constructor

        elif parent_constr:
            cl = lookupclass(node.node.expr, getmv())
            self.append(namespaceclass(cl)+'::'+node.node.attrname+'(')

        elif direct_call: # XXX no namespace (e.g., math.pow), check nr of args
            if ident == 'float' and node.args and self.mergeinh[node.args[0]] == set([(defclass('float_'), 0)]):
                self.visit(node.args[0], func)
                return
            if ident in ['abs', 'int', 'float', 'str', 'dict', 'tuple', 'list', 'type', 'cmp', 'sum', 'zip']:
                self.append('__'+ident+'(')
            elif ident in ['min', 'max', 'iter', 'round']:
                self.append('___'+ident+'(')
            elif ident == 'bool':
                self.bool_test(node.args[0], func, always_wrap=True)
                return
            elif ident == 'pow' and direct_call.mv.module.ident == 'builtin':
                if nrargs==3: third = node.args[2]
                else: third = None
                self.power(node.args[0], node.args[1], third, func)
                return
            elif ident == 'hash':
                self.append('hasher(') # XXX cleanup
            elif ident == 'isinstance' and isinstance(node.args[1], Name) and node.args[1].name in ['float','int']:
                error("'isinstance' cannot be used with ints or floats; assuming always true", node, warning=True)
                self.append('1')
                return
            else:
                if ident in self.module.mv.ext_funcs: # XXX using as? :P
                     ident = self.module.mv.ext_funcs[ident].ident

                if isinstance(node.node, Name): # XXX ugly
                    self.append(self.cpp_name(ident, func))
                else:
                    self.visit(node.node)
                self.append('(')

        elif method_call:
            for cl, _ in self.mergeinh[objexpr]:
                if isinstance(cl, class_) and cl.ident != 'none' and ident not in cl.funcs:
                    conv = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'none'}
                    clname = conv.get(cl.ident, cl.ident)
                    error("class '%s' has no method '%s'" % (clname, ident), node, warning=True)

            # tuple2.__getitem -> __getfirst__/__getsecond
            if ident == '__getitem__' and isinstance(node.args[0], Const) and node.args[0].value in (0,1) and self.only_classes(objexpr, ('tuple2',)):
                self.visit(node.node.expr, func)
                self.append('->%s()' % ['__getfirst__', '__getsecond__'][node.args[0].value])
                return

            self.visitm(node.node, '(', func)

        else:
            error("unbound identifier '"+ident+"'", node)

        if not funcs:
            if constructor: self.append(')')
            self.append(')')
            return

        self.visit_callfunc_args(funcs, node, func)

        self.append(')')
        if constructor:
            self.append(')')

    def bool_test(self, node, func, always_wrap=False):
        wrapper = always_wrap or not self.only_classes(node, ('int_', 'bool_'))
        if node in getgx().bool_test_only:
            self.visit(node, func)
        elif wrapper:
            self.append('___bool(')
            self.visit(node, func)
            is_func = bool([1 for t in self.mergeinh[node] if isinstance(t[0], function)])
            self.append(('', '!=NULL')[is_func]+')') # XXX
        else:
            self.bool_wrapper[node] = True
            self.visit(node, func)

    def visit_callfunc_args(self, funcs, node, func):
        objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(node)
        target = funcs[0] # XXX

        print_function = self.library_func(funcs, 'builtin', None, 'print')

        castnull = False # XXX
        if (self.library_func(funcs, 'random', None, 'seed') or \
            self.library_func(funcs, 'random', None, 'triangular') or \
            self.library_func(funcs, 'random', 'Random', 'seed') or \
            self.library_func(funcs, 'random', 'Random', 'triangular')):
            castnull = True
        for itertools_func in ['islice', 'izip_longest', 'permutations']:
            if self.library_func(funcs, 'itertools', None, itertools_func):
                castnull = True
                break

        for f in funcs:
            if len(f.formals) != len(target.formals):
                error('calling functions with different numbers of arguments', node, warning=True)
                self.append(')')
                return

        if parent_constr and target.inherited_from: # XXX
            target = target.inherited_from

        pairs, rest = connect_actual_formal(node, target, parent_constr, check_error=True, merge=self.mergeinh)
        if isinstance(func, function) and func.lambdawrapper:
            rest = func.largs

        if target.node.varargs:
            self.append('%d' % rest)
            if rest or pairs:
                self.append(', ')

        double = False
        if ident in ['min', 'max']:
            for arg in node.args:
                if arg in self.mergeinh and (defclass('float_'),0) in self.mergeinh[arg]:
                    double = True

        self.add_args_arg(node, funcs)

        if isinstance(func, function) and func.largs != None:
            kw = [p for p in pairs if p[1].name.startswith('__kw_')]
            nonkw = [p for p in pairs if not p[1].name.startswith('__kw_')]
            pairs = kw+nonkw[:func.largs]

        for (arg, formal) in pairs:
            cast = False
            builtin_cast = self.cast_to_builtin(arg, func, formal, target, method_call, objexpr)

            if double and self.mergeinh[arg] == set([(defclass('int_'),0)]):
                cast = True
                self.append('((double)(')
            elif builtin_cast:
                cast = True
                self.append('(('+builtin_cast+')(')
            elif not target.mv.module.builtin and assign_needs_cast(arg, func, formal, target): # XXX builtin (dict.fromkeys?)
                cast = True
                self.append('(('+typesetreprnew(formal, target)+')(')
            elif castnull and isinstance(arg, Name) and arg.name == 'None':
                cast = True
                self.append('((void *)(')

            if print_function and not formal.name.startswith('__kw_'):
                types = [t[0].ident for t in self.mergeinh[arg]]
                if 'float_' in types or 'int_' in types or 'bool_' in types:
                    cast = True
                    self.append('___box((')

            if arg in target.mv.defaults:
                if self.mergeinh[arg] == set([(defclass('none'),0)]):
                    self.append('NULL')
                elif target.mv.module == getmv().module:
                    self.append('default_%d' % (target.mv.defaults[arg]))
                else:
                    self.append('%s::default_%d' % ('__'+'__::__'.join(target.mv.module.mod_path)+'__', target.mv.defaults[arg]))

            elif arg in self.consts:
                self.append(self.consts[arg])
            else:
                if constructor and ident in ['set', 'frozenset'] and typesetreprnew(arg, func) in ['list<void *> *', 'tuple<void *> *', 'pyiter<void *> *', 'pyseq<void *> *', 'pyset<void *>']: # XXX to needs_cast
                    pass # XXX assign_needs_cast
                else:
                    self.refer(arg, func)

            if cast:
                self.append('))')
            if (arg, formal) != pairs[-1]:
                self.append(', ')

        if constructor and ident == 'frozenset':
            if pairs: self.append(',')
            self.append('1')

    def cast_to_builtin(self, arg, func, formal, target, method_call, objexpr):
        # type inference cannot deduce all necessary casts to builtin formals
        vars = {'u': 'unit', 'v': 'value', 'o': None}
        if target.mv.module.builtin and method_call and formal.name in vars and target.parent.ident in ('list', 'dict', 'set'):
            to_ts = typesetreprnew(objexpr, func, var=vars[formal.name])
            if typesetreprnew(arg, func) != to_ts:
                return to_ts

    def cast_to_builtin2(self, arg, func, objexpr, msg, formal_nr):
        # shortcut for outside of visitCallFunc XXX merge with visitCallFunc?
        cls = [t[0] for t in self.mergeinh[objexpr] if isinstance(t[0], class_)]
        if cls:
            cl = cls.pop()
            if msg in cl.funcs:
                target = cl.funcs[msg]
                if formal_nr < len(target.formals):
                    formal = target.vars[target.formals[formal_nr]]
                    return self.cast_to_builtin(arg, func, formal, target, True, objexpr)

    def visitReturn(self, node, func=None):
        if func.isGenerator:
            self.output('__stop_iteration = true;')
            self.output('return 0;')
            return
        self.return_expr(node.value, func.retnode, func)

    def return_expr(self, expr, retnode, func, yield_=False):
        if yield_:
            self.start('__result = ')
        else:
            self.start('return ')
        cast = assign_needs_cast(expr, func, retnode.thing, func)
        if cast:
            self.append('(('+typesetreprnew(retnode.thing, func)+')(')

        elif isinstance(expr, Name) and expr.name == 'self': # XXX integrate with assign_needs_cast!? # XXX self?
            lcp = lowest_common_parents(polymorphic_t(self.mergeinh[retnode.thing])) # XXX simplify
            if lcp:
                cl = lcp[0] # XXX simplify
                if not (cl == func.parent or cl in func.parent.ancestors()):
                    self.append('('+cl.ident+' *)')

        self.visit(expr, func)
        if cast: self.append('))')
        self.eol()
        if yield_:
            self.output('return __result;')

    def tuple_assign(self, lvalue, rvalue, func):
        temp = getmv().tempcount[lvalue]
        if isinstance(lvalue, tuple): nodes = lvalue
        else: nodes = lvalue.nodes

        # --- nested unpacking assignment: a, (b,c) = d, e
        if [item for item in nodes if not isinstance(item, AssName)]:
            self.start(temp+' = ')
            if isinstance(rvalue, str):
                self.append(rvalue)
            else:
                self.visit(rvalue, func)
            self.eol()

            for i, item in enumerate(nodes):
                selector = self.get_selector(temp, item, i)
                if isinstance(item, AssName):
                    self.output('%s = %s;' % (item.name, selector))
                elif isinstance(item, (AssTuple, AssList)): # recursion
                    self.tuple_assign(item, selector, func)
                elif isinstance(item, Subscript):
                    self.assign_pair(item, selector, func)
                elif isinstance(item, AssAttr):
                    self.assign_pair(item, selector, func)
                    self.eol(' = ' + selector)

        # --- non-nested unpacking assignment: a,b,c = d
        else:
            self.start()
            self.visitm(temp, ' = ', rvalue, func)
            self.eol()
            for i, item in enumerate(lvalue.nodes):
                self.start()
                self.visitm(item, ' = ', self.get_selector(temp, item, i), func)
                self.eol()

    def one_class(self, node, names):
        for clname in names:
            if self.only_classes(node, (clname,)):
                return True
        return False

    def get_selector(self, temp, item, i):
        rvalue_node = getgx().item_rvalue[item]
        sel = '__getitem__(%d)' % i
        if i < 2 and self.only_classes(rvalue_node, ('tuple2',)):
            sel = ['__getfirst__()', '__getsecond__()'][i]
        elif self.one_class(rvalue_node, ('list', 'str_', 'tuple')):
            sel = '__getfast__(%d)' % i
        return '%s->%s' % (temp, sel)

    def subs_assign(self, lvalue, func):
        if len(lvalue.subs) > 1:
            subs = inode(lvalue.expr).faketuple
        else:
            subs = lvalue.subs[0]
        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), '__setitem__(', subs, ', ', func)

    def visitAssign(self, node, func=None):
        #temp vars
        if len(node.nodes) > 1 or isinstance(node.expr, Tuple):
            if isinstance(node.expr, Tuple):
                if [n for n in node.nodes if isinstance(n, AssTuple)]: # XXX a,b=d[i,j]=..?
                    for child in node.expr.nodes:
                        if not (child,0,0) in getgx().cnode: # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not isinstance(child, Const) and not (isinstance(child, Name) and child.name == 'None'):
                            self.start(getmv().tempcount[child]+' = ')
                            self.visit(child, func)
                            self.eol()
            elif not isinstance(node.expr, Const) and not (isinstance(node.expr, Name) and node.expr.name == 'None'):
                self.start(getmv().tempcount[node.expr]+' = ')
                self.visit(node.expr, func)
                self.eol()

        # a = (b,c) = .. = expr
        right = node.expr
        for left in node.nodes:
            pairs = assign_rec(left, node.expr)
            tempvars = len(pairs) > 1

            for (lvalue, rvalue) in pairs:
                cast = None
                self.start('') # XXX remove?

                # expr[expr] = expr
                if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
                    self.assign_pair(lvalue, rvalue, func)
                    continue

                # expr.attr = expr
                elif isinstance(lvalue, AssAttr):
                    lcp = lowest_common_parents(polymorphic_t(self.mergeinh[lvalue.expr]))
                    # property
                    if len(lcp) == 1 and isinstance(lcp[0], class_) and lvalue.attrname in lcp[0].properties:
                        self.visitm(lvalue.expr, '->'+self.cpp_name(lcp[0].properties[lvalue.attrname][1])+'(', rvalue, ')', func)
                        self.eol()
                        continue
                    cast = self.var_assign_needs_cast(lvalue, rvalue, func)
                    self.assign_pair(lvalue, rvalue, func)
                    self.append(' = ')

                # name = expr
                elif isinstance(lvalue, AssName):
                    cast = self.var_assign_needs_cast(lvalue, rvalue, func)
                    self.visit(lvalue, func)
                    self.append(' = ')

                # (a,(b,c), ..) = expr
                elif isinstance(lvalue, (AssTuple, AssList)):
                    self.tuple_assign(lvalue, rvalue, func)
                    continue

                # expr[a:b] = expr
                elif isinstance(lvalue, Slice):
                    if isinstance(rvalue, Slice) and lvalue.upper == rvalue.upper == None and lvalue.lower == rvalue.lower == None:
                        self.visitm(lvalue.expr, self.connector(lvalue.expr, func), 'units = ', rvalue.expr, self.connector(rvalue.expr, func), 'units', func)
                    else:
                        fakefunc = inode(lvalue.expr).fakefunc
                        self.visitm('(', fakefunc.node.expr, ')->__setslice__(', fakefunc.args[0], ',', fakefunc.args[1], ',', fakefunc.args[2], ',', fakefunc.args[3], ',', func)
                        cast = self.var_assign_needs_cast(lvalue.expr, rvalue, func)
                        if cast: self.visitm('(('+cast+')', fakefunc.args[4], '))', func)
                        else: self.visitm(fakefunc.args[4], ')', func)
                    self.eol()
                    continue

                # expr[a:b:c] = expr
                elif isinstance(lvalue, Subscript) and isinstance(lvalue.subs[0], Sliceobj):
                    self.visit(inode(lvalue.expr).fakefunc, func)
                    self.eol()
                    continue

                # rvalue, optionally with cast
                if cast:
                    self.append('(('+cast+')(')
                if rvalue in getmv().tempcount:
                    self.append(getmv().tempcount[rvalue])
                else:
                    self.visit(rvalue, func)
                if cast: self.append('))')

                self.eol()

    def var_assign_needs_cast(self, expr, rvalue, func):
        cast = None
        if isinstance(expr, AssName):
            var = lookupvar(expr.name, func)
            if assign_needs_cast(rvalue, func, var, func):
                cast = typesetreprnew(var, func)
        elif isinstance(expr, AssAttr):
            lcp = lowest_common_parents(polymorphic_t(self.mergeinh[expr.expr]))
            if len(lcp) == 1 and isinstance(lcp[0], class_):
                var = lookupvar(expr.attrname, lcp[0])
                if assign_needs_cast(rvalue, func, var, lcp[0]):
                    cast = typesetreprnew(var, lcp[0])
        else:
            if assign_needs_cast(rvalue, func, expr, func):
                cast = typesetreprnew(expr, func)
        return cast

    def assign_pair(self, lvalue, rvalue, func):
        self.start('')

        # expr[expr] = expr
        if isinstance(lvalue, Subscript) and not isinstance(lvalue.subs[0], Sliceobj):
            self.subs_assign(lvalue, func)
            if isinstance(rvalue, str):
                self.append(rvalue)
            elif rvalue in getmv().tempcount:
                self.append(getmv().tempcount[rvalue])
            else:
                cast = self.cast_to_builtin2(rvalue, func, lvalue.expr, '__setitem__', 2)
                if cast: self.append('((%s)' % cast)
                self.visit(rvalue, func)
                if cast: self.append(')')
            self.append(')')
            self.eol()

        # expr.x = expr
        elif isinstance(lvalue, AssAttr):
            self.visitAssAttr(lvalue, func)

    def do_lambdas(self, declare):
        for l in getmv().lambdas.values():
            if l.ident not in getmv().funcs:
                self.visitFunction(l.node, declare=declare)

    def do_listcomps(self, declare):
        for (listcomp, lcfunc, func) in getmv().listcomps: # XXX cleanup
            if lcfunc.mv.module.builtin:
                continue

            parent = func
            while isinstance(parent, function) and parent.listcomp:
                parent = parent.parent

            if isinstance(parent, function):
                if not self.inhcpa(parent) or parent.inherited:
                    continue

            genexpr = listcomp in getgx().genexp_to_lc.values()
            if declare:
                self.listcomp_head(listcomp, True, genexpr)
            elif genexpr:
                self.genexpr_class(listcomp, declare)
            else:
                self.listcomp_func(listcomp)

    def listcomp_head(self, node, declare, genexpr):
        lcfunc, func = self.listcomps[node]
        args = [a+b for a,b in self.lc_args(lcfunc, func)]
        ts = typesetreprnew(node, lcfunc)
        if not ts.endswith('*'): ts += ' '
        if genexpr:
            self.genexpr_class(node, declare)
        else:
            self.output('static inline '+ts+lcfunc.ident+'('+', '.join(args)+')'+[' {', ';'][declare])

    def lc_args(self, lcfunc, func):
        args = []
        for name in lcfunc.misses:
            if lookupvar(name, func).parent:
                args.append((typesetreprnew(lookupvar(name, lcfunc), lcfunc), self.cpp_name(name)))
        return args

    def listcomp_func(self, node):
        lcfunc, func = self.listcomps[node]
        self.listcomp_head(node, False, False)
        self.indent()
        self.lc_locals(lcfunc)
        self.output(typesetreprnew(node, lcfunc)+'__ss_result = new '+typesetreprnew(node, lcfunc)[:-2]+'();\n')
        self.listcomp_rec(node, node.quals, lcfunc, False)
        self.output('return __ss_result;')
        self.deindent();
        self.output('}\n')

    def genexpr_class(self, node, declare):
        lcfunc, func = self.listcomps[node]
        args = self.lc_args(lcfunc, func)
        func1 = lcfunc.ident+'('+', '.join([a+b for a,b in args])+')'
        func2 = typesetreprnew(node, lcfunc)[7:-3]
        if declare:
            ts = typesetreprnew(node, lcfunc)
            if not ts.endswith('*'): ts += ' '
            self.output('class '+lcfunc.ident+' : public '+ts[:-2]+' {')
            self.output('public:')
            self.indent()
            self.lc_locals(lcfunc)
            for a,b in args:
                self.output(a+b+';');
            self.output('int __last_yield;\n')
            self.output(func1+';')
            self.output(func2+' __get_next();')
            self.deindent();
            self.output('};\n')
        else:
            self.output(lcfunc.ident+'::'+func1+' {')
            for a,b in args:
                self.output('    this->%s = %s;' % (b,b))
            self.output('    __last_yield = -1;')
            self.output('}\n')
            self.output(func2+' '+lcfunc.ident+'::__get_next() {')
            self.indent();
            self.output('if(!__last_yield) goto __after_yield_0;')
            self.output('__last_yield = 0;\n')
            self.listcomp_rec(node, node.quals, lcfunc, True)
            self.output('__stop_iteration = true;')
            self.deindent();
            self.output('}\n')

    def lc_locals(self, lcfunc):
        decl = {}
        for (name,var) in lcfunc.vars.items(): # XXX merge with visitFunction
            name = self.cpp_name(name)
            decl.setdefault(typesetreprnew(var, lcfunc), []).append(name)
        for ts, names in decl.items():
            if ts.endswith('*'):
                self.output(ts+', *'.join(names)+';')
            else:
                self.output(ts+', '.join(names)+';')

    def fastfor_switch(self, node, func):
        self.start()
        for arg in node.list.args:
            if arg in getmv().tempcount:
                self.start()
                self.visitm(getmv().tempcount[arg], ' = ', arg, func)
                self.eol()
        self.start('if(')
        if node.list.args[2] in getmv().tempcount:
            self.append(getmv().tempcount[node.list.args[2]])
        else:
            self.visit(node.list.args[2])
        self.append('>0) {')
        print >>self.out, self.line

    # --- nested for loops: loop headers, if statements
    def listcomp_rec(self, node, quals, lcfunc, genexpr):
        if not quals:
            if genexpr:
                self.start('__result = ')
                self.visit(node.expr, lcfunc)
                self.eol()
                self.output('return __result;')
                self.start('__after_yield_0:')
            elif len(node.quals) == 1 and not fastfor(node.quals[0]) and not self.fastenum(node.quals[0]) and not self.fastzip2(node.quals[0]) and not node.quals[0].ifs and self.one_class(node.quals[0].list, ('tuple', 'list', 'str_', 'dict','set')):
                self.start('__ss_result->units['+getmv().tempcount[node.quals[0].list]+'] = ')
                self.visit(node.expr, lcfunc)
            else:
                self.start('__ss_result->append(')
                self.visit(node.expr, lcfunc)
                self.append(')')
            self.eol()
            return

        qual = quals[0]

        # iter var
        if isinstance(qual.assign, AssName):
            var = lookupvar(qual.assign.name, lcfunc)
        else:
            var = lookupvar(getmv().tempcount[qual.assign], lcfunc)
        iter = self.cpp_name(var.name)

        if fastfor(qual):
            self.do_fastfor(node, qual, quals, iter, lcfunc, genexpr)
        elif self.fastenum(qual):
            self.do_fastenum(qual, lcfunc, genexpr)
            self.listcompfor_body(node, quals, iter, lcfunc, True, genexpr)
        elif self.fastzip2(qual):
            self.do_fastzip2(qual, lcfunc, genexpr)
            self.listcompfor_body(node, quals, iter, lcfunc, True, genexpr)
        else:
            if not isinstance(qual.list, Name):
                itervar = getmv().tempcount[qual]
                self.start('')
                self.visitm(itervar, ' = ', qual.list, lcfunc)
                self.eol()
            else:
                itervar = self.cpp_name(qual.list.name)

            pref, tail = self.forin_preftail(qual)

            if len(node.quals) == 1 and not qual.ifs and not genexpr:
                if self.one_class(qual.list, ('list', 'tuple', 'str_', 'dict', 'set')):
                    self.output('__ss_result->resize(len('+itervar+'));')

            self.start('FOR_IN'+pref+'('+iter+','+itervar+','+tail)
            print >>self.out, self.line+')'
            self.listcompfor_body(node, quals, iter, lcfunc, False, genexpr)

    def do_fastfor(self, node, qual, quals, iter, func, genexpr):
        if len(qual.list.args) == 3 and not const_literal(qual.list.args[2]):
            self.fastfor_switch(qual, func)
            self.indent()
            self.fastfor(qual, iter, '', func)
            self.forbody(node, quals, iter, func, False, genexpr)
            self.deindent()
            self.output('} else {')
            self.indent()
            self.fastfor(qual, iter, '_NEG', func)
            self.forbody(node, quals, iter, func, False, genexpr)
            self.deindent()
            self.output('}')
        else:
            neg=''
            if len(qual.list.args) == 3 and const_literal(qual.list.args[2]) and isinstance(qual.list.args[2], UnarySub):
                neg = '_NEG'
            self.fastfor(qual, iter, neg, func)
            self.forbody(node, quals, iter, func, False, genexpr)

    def listcompfor_body(self, node, quals, iter, lcfunc, skip, genexpr):
        qual = quals[0]

        if not skip:
            self.indent()
            if isinstance(qual.assign, (AssTuple, AssList)):
                self.tuple_assign(qual.assign, iter, lcfunc)

        # if statements
        if qual.ifs:
            self.start('if (')
            self.indent()
            for cond in qual.ifs:
                self.bool_test(cond.test, lcfunc)
                if cond != qual.ifs[-1]:
                    self.append(' && ')
            self.append(') {')
            print >>self.out, self.line

        # recurse
        self.listcomp_rec(node, quals[1:], lcfunc, genexpr)

        # --- nested for loops: loop tails
        if qual.ifs:
            self.deindent();
            self.output('}')
        self.deindent();
        self.output('END_FOR\n')

    def visitGenExpr(self, node, func=None):
        self.visit(getgx().genexp_to_lc[node], func)

    def visitListComp(self, node, func=None):
        lcfunc, _ = self.listcomps[node]
        args = []
        temp = self.line

        for name in lcfunc.misses:
            var = lookupvar(name, func)
            if var.parent:
                if name == 'self' and not func.listcomp: # XXX parent?
                    args.append('this')
                else:
                    args.append(self.cpp_name(name))

        self.line = temp
        if node in getgx().genexp_to_lc.values():
            self.append('new ')
        self.append(lcfunc.ident+'('+', '.join(args)+')')

    def visitSubscript(self, node, func=None):
        if node.flags == 'OP_DELETE':
            self.start()
            if isinstance(node.subs[0], Sliceobj):
                self.visitCallFunc(inode(node.expr).fakefunc, func)
            else:
                self.visitCallFunc(inode(node.expr).fakefunc, func)
            self.eol()
        else:
            self.visitCallFunc(inode(node.expr).fakefunc, func)

    def visitMod(self, node, func=None):
        # --- non-str % ..
        if [t for t in getgx().merged_inh[node.left] if t[0].ident != 'str_']:
            self.visitBinary(node.left, node.right, '__mod__', '%', func)
            return

        # --- str % non-constant dict/tuple
        if not isinstance(node.right, (Tuple, Dict)) and node.right in getgx().merged_inh: # XXX
            if [t for t in getgx().merged_inh[node.right] if t[0].ident == 'dict']:
                self.visitm('__moddict(', node.left, ', ', node.right, ')', func)
                return
            elif [t for t in getgx().merged_inh[node.right] if t[0].ident in ['tuple', 'tuple2']]:
                self.visitm('__modtuple(', node.left, ', ', node.right, ')', func)
                return

        # --- str % constant-dict:
        if isinstance(node.right, Dict): # XXX geen str keys
            self.visitm('__modcd(', node.left, ', ', 'new list<str *>(%d, ' % len(node.right.items), func)
            self.append(', '.join([('new str("%s")' % key.value) for key, value in node.right.items]))
            self.append(')')
            nodes = [value for (key,value) in node.right.items]
        else:
            self.visitm('__modct(', node.left, func)
            # --- str % constant-tuple
            if isinstance(node.right, Tuple):
                nodes = node.right.nodes

            # --- str % non-tuple/non-dict
            else:
                nodes = [node.right]
            self.append(', %d' % len(nodes))

        # --- visit nodes, boxing scalars
        for n in nodes:
            if [clname for clname in ('float_', 'int_', 'bool_') if (defclass(clname), 0) in self.mergeinh[n]]:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.append(')')

    def visitPrintnl(self, node, func=None):
        self.visitPrint(node, func, print_space=False)

    def visitPrint(self, node, func=None, print_space=True):
        self.start('print2(')
        if node.dest:
            self.visitm(node.dest, ', ', func)
        if print_space: self.append('1,')
        else: self.append('0,')
        self.append(str(len(node.nodes)))
        for n in node.nodes:
            types = [t[0].ident for t in self.mergeinh[n]]
            if 'float_' in types or 'int_' in types or 'bool_' in types:
                self.visitm(', ___box(', n, ')', func)
            else:
                self.visitm(', ', n, func)
        self.eol(')')

    def visitGetattr(self, node, func=None):
        cl, module = lookup_class_module(node.expr, inode(node).mv, func)

        # module.attr
        if module:
            self.append(mod_namespace(module)+'::')

        # class.attr: staticmethod
        elif cl and node.attrname in cl.staticmethods:
            ident = cl.ident
            if cl.ident in ['dict', 'defaultdict']: # own namespace because of template vars
                self.append('__'+cl.ident+'__::')
            elif isinstance(node.expr, Getattr):
                submod = lookupmodule(node.expr.expr, inode(node).mv)
                self.append(mod_namespace(submod)+'::'+ident+'::')
            else:
                self.append(ident+'::')

        # class.attr
        elif cl: # XXX merge above?
            ident = cl.ident
            if isinstance(node.expr, Getattr):
                submod = lookupmodule(node.expr.expr, inode(node).mv)
                self.append(mod_namespace(submod)+'::'+cl.cpp_name+'::')
            else:
                self.append(ident+'::')

        # obj.attr
        else:
            for t in self.mergeinh[node.expr]:
                if isinstance(t[0], class_) and node.attrname in t[0].parent.vars:
                    error("class attribute '"+node.attrname+"' accessed without using class name", node, warning=True)
                    break

            if not isinstance(node.expr, (Name)):
                self.append('(')
            if isinstance(node.expr, Name) and not lookupvar(node.expr.name, func): # XXX XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            if not isinstance(node.expr, (Name)):
                self.append(')')

            self.append(self.connector(node.expr, func))

        ident = node.attrname

        # property
        lcp = lowest_common_parents(polymorphic_t(self.mergeinh[node.expr]))
        if len(lcp) == 1 and isinstance(lcp[0], class_) and node.attrname in lcp[0].properties:
            self.append(self.cpp_name(lcp[0].properties[node.attrname][0])+'()')
            return

        # getfast
        if ident == '__getitem__' and self.one_class(node.expr, ('list', 'str_', 'tuple')):
            ident = '__getfast__'

        self.append(self.cpp_name(ident))

    def visitAssAttr(self, node, func=None): # XXX merge with visitGetattr
        cl, module = lookup_class_module(node.expr, inode(node).mv, func)

        # module.attr
        if module:
            self.append(mod_namespace(module)+'::')

        # class.attr
        elif cl:
            if isinstance(node.expr, Getattr):
                submod = lookupmodule(node.expr.expr, inode(node).mv)
                self.append(mod_namespace(submod)+'::'+cl.cpp_name+'::')
            else:
                self.append(cl.ident+'::')

        # obj.attr
        else:
            if isinstance(node.expr, Name) and not lookupvar(node.expr.name, func): # XXX
                self.append(node.expr.name)
            else:
                self.visit(node.expr, func)
            self.append(self.connector(node.expr, func)) # XXX '->'

        self.append(self.cpp_name(node.attrname))

    def visitAssName(self, node, func=None):
        self.append(self.cpp_name(node.name))

    def visitName(self, node, func=None, add_cl=True):
        map = {'True': 'True', 'False': 'False', 'self': 'this'}
        if node in getmv().lwrapper:
            self.append(getmv().lwrapper[node])
        elif node.name == 'None':
            self.append('NULL')
        elif node.name == 'self' and \
            ((not func or func.listcomp or not isinstance(func.parent, class_)) or \
             (func and func.parent and func.isGenerator)): # XXX lookupvar?
            self.append('self')
        elif node.name in map:
            self.append(map[node.name])

        else: # XXX clean up
            if not self.mergeinh[node] and not inode(node).parent in getgx().inheritance_relations:
                error("variable '"+node.name+"' has no type", node, warning=True)
                self.append(node.name)
            elif singletype(node, module):
                self.append('__'+singletype(node, module).ident+'__')
            else:
                if (defclass('class_'),0) in self.mergeinh[node]:
                    self.append('cl_'+node.name)
                elif add_cl and [t for t in self.mergeinh[node] if isinstance(t[0], static_class)]:
                    self.append('cl_'+node.name)
                else:
                    if isinstance(func, class_) and node.name in func.parent.vars: # XXX
                        self.append(func.ident+'::')
                    self.append(self.cpp_name(node.name))

    def expandspecialchars(self, value):
        value = list(value)
        replace = dict(['\\\\', '\nn', '\tt', '\rr', '\ff', '\bb', '\vv', '""'])

        for i in range(len(value)):
            if value[i] in replace:
                value[i] = '\\'+replace[value[i]]
            elif value[i] not in string.printable:
                value[i] = '\\'+oct(ord(value[i])).zfill(4)[1:]

        return ''.join(value)

    def visitConst(self, node, func=None):
        if not self.filling_consts and isinstance(node.value, str):
            self.append(self.get_constant(node))
            return

        if node.value == None:
            self.append('NULL')
            return

        t = list(inode(node).types())[0]

        if t[0].ident == 'int_':
            self.append(str(node.value))
            if getgx().longlong:
                self.append('LL')
        elif t[0].ident == 'float_':
            if str(node.value) in ['inf', '1.#INF', 'Infinity']: self.append('INFINITY')
            elif str(node.value) in ['-inf', '-1.#INF', 'Infinity']: self.append('-INFINITY')
            else: self.append(str(node.value))
        elif t[0].ident == 'str_':
            self.append('new str("%s"' % self.expandspecialchars(node.value))
            if '\0' in node.value: # '\0' delimiter in C
                self.append(', %d' % len(node.value))
            self.append(')')
        elif t[0].ident == 'complex':
            self.append('new complex(%s, %s)' % (node.value.real, node.value.imag))
        else:
            self.append('new %s(%s)' % (t[0].ident, node.value))

# --- helper functions

def singletype(node, type):
    types = [t[0] for t in inode(node).types()]
    if len(types) == 1 and isinstance(types[0], type):
        return types[0]

def singletype2(types, type):
    ltypes = list(types)
    if len(types) == 1 and isinstance(ltypes[0][0], type):
        return ltypes[0][0]

def mod_namespace(module):
    return '__'+'__::__'.join(module.mod_path)+'__'

def namespaceclass(cl):
    module = cl.mv.module

    if module.ident != 'builtin' and module != getmv().module and module.mod_path:
        return mod_namespace(module)+'::'+nokeywords(cl.ident)
    else:
        return nokeywords(cl.ident)

# --- determine representation of node type set (within parameterized context)
def typesetreprnew(node, parent, cplusplus=True, check_extmod=False, check_ret=False, var=None):
    orig_parent = parent
    while is_listcomp(parent): # XXX redundant with typesplit?
        parent = parent.parent

    if cplusplus and isinstance(node, variable) and node.looper:
        return typesetreprnew(node.looper, parent, cplusplus)[:-2]+'::for_in_loop '

    # --- separate types in multiple duplicates, so we can do parallel template matching of subtypes..
    split = typesplit(node, parent)

    # --- use this 'split' to determine type representation
    try:
        ts = typestrnew(split, parent, cplusplus, orig_parent, node, check_extmod, 0, check_ret, var)
    except RuntimeError:
        if not hasattr(node, 'lineno'): node.lineno = None # XXX
        if not getmv().module.builtin and isinstance(node, variable) and not node.name.startswith('__'): # XXX startswith
            error("variable %s has dynamic (sub)type" % repr(node), warning=True)
        ts = 'ERROR'

    if cplusplus:
        if not ts.endswith('*'): ts += ' '
        return ts
    return '['+ts+']'

class ExtmodError(Exception):
    pass

def typestrnew(split, root_class, cplusplus, orig_parent, node=None, check_extmod=False, depth=0, check_ret=False, var=None):
    if depth==10:
        raise RuntimeError()

    # --- annotation or c++ code
    conv1 = {'int_': '__ss_int', 'float_': 'double', 'str_': 'str', 'none': 'int', 'bool_':'__ss_bool'}
    conv2 = {'int_': 'int', 'float_': 'float', 'str_': 'str', 'class_': 'class', 'none': 'None','bool_': 'bool'}
    if cplusplus: sep, ptr, conv = '<>', ' *', conv1
    else: sep, ptr, conv = '()', '', conv2

    def map(ident):
        if cplusplus: return ident+' *'
        return conv.get(ident, ident)

    # --- examine split
    alltypes = set() # XXX
    for (dcpa, cpa), types in split.items():
        alltypes.update(types)

    anon_funcs = set([t[0] for t in alltypes if isinstance(t[0], function)])
    if anon_funcs and check_extmod:
        raise ExtmodError()
    if anon_funcs:
        f = anon_funcs.pop()
        if f.mv != getmv():
            return mod_namespace(f.mv.module)+'::'+'lambda%d' % f.lambdanr
        return 'lambda%d' % f.lambdanr

    classes = polymorphic_cl(split_classes(split))
    lcp = lowest_common_parents(classes)

    # --- multiple parent classes
    if len(lcp) > 1:
        if set(lcp) == set([defclass('int_'),defclass('float_')]):
            return conv['float_']
        if inode(node) is not None and inode(node).mv.module.builtin:
            return '***ERROR*** '
        if isinstance(node, variable):
            if not node.name.startswith('__') : # XXX startswith
                if orig_parent: varname = "%s" % node
                else: varname = "'%s'" % node
                error("variable %s has dynamic (sub)type: {%s}" % (varname, ', '.join([conv2.get(cl.ident, cl.ident) for cl in lcp])), warning=True)
        elif node not in getgx().bool_test_only:
            error("expression has dynamic (sub)type: {%s}" % ', '.join([conv2.get(cl.ident, cl.ident) for cl in lcp]), node, warning=True)

    elif not classes:
        if cplusplus: return 'void *'
        return ''

    cl = lcp.pop()

    if check_ret and cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict':
        print '*WARNING* %s:defaultdicts are returned as dicts' % root_class.ident
    elif check_extmod and cl.mv.module.builtin and not (cl.mv.module.ident == 'builtin' and cl.ident in ['int_', 'float_', 'complex', 'str_', 'list', 'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'none', 'bool_']) and not (cl.mv.module.ident == 'collections' and cl.ident == 'defaultdict'):
        raise ExtmodError()

    # --- simple built-in types
    if cl.ident in ['int_', 'float_', 'bool_']:
        return conv[cl.ident]
    elif cl.ident == 'str_':
        return 'str'+ptr
    elif cl.ident == 'none':
        if cplusplus: return 'void *'
        return 'None'

    # --- namespace prefix
    namespace = ''
    if cl.module not in [getmv().module, getgx().modules['builtin']] and not (cl.ident in getmv().ext_funcs or cl.ident in getmv().ext_classes):
        if cplusplus: namespace = '__'+'__::__'.join([n for n in cl.module.mod_path])+'__::'
        else: namespace = '::'.join([n for n in cl.module.mod_path])+'::'

        if cl.module.filename.endswith('__init__.py'): # XXX only pass cl.module
            include = '/'.join(cl.module.mod_path)+'/__init__.hpp'
        else:
            include = '/'.join(cl.module.mod_path)+'.hpp'
        getmv().module.prop_includes.add(include)

    template_vars = cl.tvar_names()
    if template_vars:
        subtypes = []
        for tvar in template_vars:
            subsplit = split_subsplit(split, tvar)
            ts = typestrnew(subsplit, root_class, cplusplus, orig_parent, node, check_extmod, depth+1)
            if tvar == var:
                return ts
            for (dcpa, cpa), types in subsplit.items():
                if [t[0] for t in types if isinstance(t[0], function)]:
                    ident = cl.ident
                    if ident == 'tuple2': ident = 'tuple'
                    error("'%s' instance containing function reference" % ident, node, warning=True)
            subtypes.append(ts)
    else:
        if cl.ident in getgx().cpp_keywords:
            return namespace+getgx().ss_prefix+map(cl.ident)
        return namespace+map(cl.ident)

    ident = cl.ident

    # --- binary tuples
    if ident == 'tuple2':
        if subtypes[0] == subtypes[1]:
            ident, subtypes = 'tuple', [subtypes[0]]
    if ident == 'tuple2' and not cplusplus:
        ident = 'tuple'
    elif ident == 'tuple' and cplusplus:
        return namespace+'tuple2'+sep[0]+subtypes[0]+', '+subtypes[0]+sep[1]+ptr

    if ident in ['frozenset', 'pyset'] and cplusplus:
        ident = 'set'

    if ident in getgx().cpp_keywords:
        ident = getgx().ss_prefix+ident

    # --- final type representation
    return namespace+ident+sep[0]+', '.join(subtypes)+sep[1]+ptr

# --- separate types in multiple duplicates
def typesplit(node, parent):
    split = {}

    if isinstance(parent, function) and parent in getgx().inheritance_relations:
        if node in getgx().merged_inh:
            split[1,0] = getgx().merged_inh[node]
        return split

    while is_listcomp(parent):
        parent = parent.parent

    if isinstance(parent, class_): # class variables
        for dcpa in range(parent.dcpa):
            if (node, dcpa, 0) in getgx().cnode:
                split[dcpa, 0] = getgx().cnode[node, dcpa, 0].types()

    elif isinstance(parent, function):
        if isinstance(parent.parent, class_): # method variables/expressions (XXX nested functions)
            for dcpa in range(parent.parent.dcpa):
                if dcpa in parent.cp:
                    for cpa in range(len(parent.cp[dcpa])):
                        if (node, dcpa, cpa) in getgx().cnode:
                            split[dcpa, cpa] = getgx().cnode[node, dcpa, cpa].types()

        else: # function variables/expressions
            if 0 in parent.cp:
                for cpa in range(len(parent.cp[0])):
                    if (node, 0, cpa) in getgx().cnode:
                        split[0, cpa] = getgx().cnode[node, 0, cpa].types()
    else:
        split[0, 0] = inode(node).types()

    return split

def polymorphic_cl(classes):
    cls = set([cl for cl in classes])
    if len(cls) > 1 and defclass('none') in cls and not defclass('int_') in cls and not defclass('float_') in cls and not defclass('bool_') in cls:
        cls.remove(defclass('none'))
#    if defclass('float_') in cls and defclass('int_') in cls:
#        cls.remove(defclass('int_'))
    if defclass('tuple2') in cls and defclass('tuple') in cls: # XXX hmm
        cls.remove(defclass('tuple2'))
    return cls

def split_classes(split):
    alltypes = set()
    for (dcpa, cpa), types in split.items():
        alltypes.update(types)
    return set([t[0] for t in alltypes if isinstance(t[0], class_)])

# --- determine lowest common parent classes (inclusive)
def lowest_common_parents(classes):
    lcp = set(classes)

    changed = 1
    while changed:
        changed = 0
        for cl in getgx().allclasses:
             desc_in_classes = [[c for c in ch.descendants(inclusive=True) if c in lcp] for ch in cl.children]
             if len([d for d in desc_in_classes if d]) > 1:
                 for d in desc_in_classes:
                     lcp.difference_update(d)
                 lcp.add(cl)
                 changed = 1

    for cl in lcp.copy():
        if isinstance(cl, class_): # XXX
            lcp.difference_update(cl.descendants())

    result = [] # XXX there shouldn't be doubles
    for cl in lcp:
        if cl.ident not in [r.ident for r in result]:
            result.append(cl)
    return result

def hmcpa(func):
    got_one = 0
    for dcpa, cpas in func.cp.items():
        if len(cpas) > 1: return len(cpas)
        if len(cpas) == 1: got_one = 1
    return got_one

# --- assignment (incl. passing arguments, returning values) may require a cast
def assign_needs_cast(arg, func, formal, target):
    argsplit = typesplit(arg, func)
    formalsplit = typesplit(formal, target)

    try:
        return assign_needs_cast_rec(argsplit, func, formalsplit, target)
    except RuntimeError:
        return False

def assign_needs_cast_rec(argsplit, func, formalsplit, target, depth=0):
    if depth == 10:
        raise RuntimeError()

    argclasses = split_classes(argsplit)
    formalclasses = split_classes(formalsplit)

    # void *
    noneset = set([defclass('none')])
    if argclasses == noneset and formalclasses != noneset:
        return True

    # no type
    if not argclasses and formalclasses: # a = [[]]
        return True

    if defclass('none') in formalclasses:
        formalclasses.remove(defclass('none'))
    if defclass('tuple2') in formalclasses and defclass('tuple') in formalclasses: # XXX generalize? lcp?
        formalclasses.remove(defclass('tuple'))
    if len(formalclasses) != 1:
        return False

    cl = formalclasses.pop()

    tvars = cl.tvar_names()
    if tvars:
        for tvar in tvars:
            argsubsplit = split_subsplit(argsplit, tvar)
            formalsubsplit = split_subsplit(formalsplit, tvar)
            if assign_needs_cast_rec(argsubsplit, func, formalsubsplit, target, depth+1):
                return True
    return False

def split_subsplit(split, varname):
    subsplit = {}
    for (dcpa, cpa), types in split.items():
        subsplit[dcpa, cpa] = set()
        for t in types:
            if not varname in t[0].vars: # XXX
                continue
            var = t[0].vars[varname]
            if (var, t[1], 0) in getgx().cnode: # XXX yeah?
                subsplit[dcpa, cpa].update(getgx().cnode[var, t[1], 0].types())
    return subsplit

def polymorphic_t(types):
    return polymorphic_cl([t[0] for t in types])

# --- number classes with low and high numbers, to enable constant-time subclass check
def number_classes():
    counter = 0
    for cl in getgx().allclasses:
        if not cl.bases:
            counter = number_class_rec(cl, counter+1)

def number_class_rec(cl, counter):
    cl.low = counter
    for child in cl.children:
        counter = number_class_rec(child, counter+1)
    cl.high = counter
    return counter

class Bitpair:
    def __init__(self, nodes, msg, inline):
        self.nodes = nodes
        self.msg = msg
        self.inline = inline

def unboxable(types):
    if not isinstance(types, set):
        types = inode(types).types()
    classes = set([t[0] for t in types])

    if [cl for cl in classes if cl.ident not in ['int_','float_','bool_']]:
        return None
    else:
        if classes:
            return classes.pop().ident
        return None

def get_includes(mod):
    imports = set()
    if mod == getgx().main_module:
        mods = getgx().modules.values()
    else:
        d = mod.mv.imports.copy()
        d.update(mod.mv.fake_imports)
        mods = d.values()

    for mod in mods:
        if mod.filename.endswith('__init__.py'): # XXX
            imports.add('/'.join(mod.mod_path)+'/__init__.hpp')
        else:
            imports.add('/'.join(mod.mod_path)+'.hpp')
    return imports

def subclass(a, b):
    if b in a.bases:
        return True
    else:
        return a.bases and subclass(a.bases[0], b) # XXX mult inh

# --- determine virtual methods and variables
def analyze_virtuals():
    for node in getgx().merged_inh: # XXX all:
        # --- for every message
        if isinstance(node, CallFunc) and not inode(node).mv.module.builtin: #ident == 'builtin':
            objexpr, ident, direct_call, method_call, constructor, parent_constr = analyze_callfunc(node)
            if not method_call or objexpr not in getgx().merged_inh:
                continue # XXX

            # --- determine abstract receiver class
            classes = polymorphic_t(getgx().merged_inh[objexpr])
            if not classes:
                continue

            if isinstance(objexpr, Name) and objexpr.name == 'self' and inode(objexpr).parent: # XXX last check to avoid crash
                abstract_cl = inode(objexpr).parent.parent
            else:
                lcp = lowest_common_parents(classes)
                lcp = [x for x in lcp if isinstance(x, class_)] # XXX
                if not lcp:
                    continue
                abstract_cl = lcp[0]

            if not abstract_cl or not isinstance(abstract_cl, class_):
                continue
            subclasses = [cl for cl in classes if subclass(cl, abstract_cl)]

            # --- register virtual method
            if not ident.startswith('__'):
                redefined = False
                for concrete_cl in classes:
                    if [cl for cl in concrete_cl.ancestors_upto(abstract_cl) if ident in cl.funcs and not cl.funcs[ident].inherited]:
                        redefined = True

                if redefined:
                    abstract_cl.virtuals.setdefault(ident, set()).update(subclasses)

            # --- register virtual var
            elif ident in ['__getattr__','__setattr__'] and subclasses:
                var = defaultvar(node.args[0].value, abstract_cl)
                abstract_cl.virtualvars.setdefault(node.args[0].value, set()).update(subclasses)

# --- merge variables assigned to via 'self.varname = ..' in inherited methods into base class
def upgrade_variables():
    for node, inheritnodes in getgx().inheritance_relations.items():
        if isinstance(node, AssAttr):
            baseclass = inode(node).parent.parent
            inhclasses = [inode(x).parent.parent for x in inheritnodes]
            var = defaultvar(node.attrname, baseclass)

            for inhclass in inhclasses:
                inhvar = lookupvar(node.attrname, inhclass)

                if (var, 1, 0) in getgx().cnode:
                    newnode = getgx().cnode[var,1,0]
                else:
                    newnode = cnode(var, 1, 0, parent=baseclass)
                    getgx().types[newnode] = set()

                if inhvar in getgx().merged_all: # XXX ?
                    getgx().types[newnode].update(getgx().merged_all[inhvar])

def nokeywords(name):
    if name in getgx().cpp_keywords:
        return getgx().ss_prefix+name
    return name

# --- generate C++ and Makefiles
def generate_code():
    print '[generating c++ code..]'

    ident = getgx().main_module.ident

    if sys.platform == 'win32':
        pyver = '%d%d' % sys.version_info[:2]
        prefix = sysconfig.get_config_var('prefix').replace('\\', '/')
    else:
        pyver = sysconfig.get_config_var('VERSION')
        includes = '-I' + sysconfig.get_python_inc() + ' ' + \
                   '-I' + sysconfig.get_python_inc(plat_specific=True)
        if sys.platform == 'darwin':
            ldflags = sysconfig.get_config_var('BASECFLAGS')
        else:
            ldflags = sysconfig.get_config_var('LIBS') + ' ' + \
                      sysconfig.get_config_var('SYSLIBS') + ' ' + \
                      '-lpython'+pyver
            if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
                ldflags += ' -L' + sysconfig.get_config_var('LIBPL')

    if getgx().extension_module:
        if sys.platform == 'win32': ident += '.pyd'
        else: ident += '.so'

    # --- generate C++ files
    mods = getgx().modules.values()
    for module in mods:
        if not module.builtin:
            # create output directory if necessary
            if getgx().output_dir:
                output_dir = os.path.join(getgx().output_dir, module.dir)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

            gv = generateVisitor(module)
            mv = module.mv
            setmv(mv)
            walk(module.ast, gv)
            gv.out.close()
            gv.header_file()
            gv.out.close()
            gv.insert_consts(declare=False)
            gv.insert_consts(declare=True)
            gv.insert_includes()

    # --- generate Makefile
    makefile = file(os.path.join(getgx().output_dir, getgx().makefile_name), 'w')

    cppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.cpp' for m in mods])
    hppfiles = ' '.join([m.filename[:-3].replace(' ', '\ ')+'.hpp' for m in mods])
    repath = connect_paths(getgx().libdir.replace(' ', '\ '), 're.cpp')
    if not repath in cppfiles:
        cppfiles += ' '+repath
        hppfiles += ' '+connect_paths(getgx().libdir.replace(' ', '\ '), 're.hpp')

    # import flags
    if getgx().flags: flags = getgx().flags
    elif os.path.isfile('FLAGS'): flags = 'FLAGS'
    elif getgx().msvc: flags = connect_paths(getgx().sysdir, 'FLAGS.nt')
    else: flags = connect_paths(getgx().sysdir, 'FLAGS')

    for line in file(flags):
        line = line[:-1]

        if line[:line.find('=')].strip() == 'CCFLAGS':
            line += ' -I. -I'+getgx().libdir.replace(' ', '\ ')
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/include'):
                line += ' -I/usr/local/include' # XXX
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/include'):
                line += ' -I/opt/local/include' # XXX
            if not getgx().wrap_around_check: line += ' -D__SS_NOWRAP'
            if not getgx().bounds_checking: line += ' -D__SS_NOBOUNDS'
            if getgx().fast_random: line += ' -D__SS_FASTRANDOM'
            if getgx().longlong: line += ' -D__SS_LONG'
            if getgx().extension_module:
                if getgx().msvc: line += ' /DLL /LIBPATH:%s/libs /LIBPATH:python%s' % (prefix, pyver)
                elif sys.platform == 'win32': line += ' -I%s/include -D__SS_BIND' % prefix
                else: line += ' -g -fPIC -D__SS_BIND ' + includes

        elif line[:line.find('=')].strip() == 'LFLAGS':
            if sys.platform == 'darwin' and os.path.isdir('/opt/local/lib'): # XXX
                line += ' -L/opt/local/lib'
            if sys.platform == 'darwin' and os.path.isdir('/usr/local/lib'): # XXX
                line += ' -L/usr/local/lib'
            if getgx().extension_module:
                if sys.platform == 'win32': line += ' -shared -L%s/libs -lpython%s' % (prefix, pyver)
                elif sys.platform == 'darwin': line += ' -bundle -undefined dynamic_lookup ' + ldflags
                elif sys.platform == 'sunos5': line += ' -shared -Xlinker ' + ldflags
                else: line += ' -shared -Xlinker -export-dynamic ' + ldflags

            if 'socket' in [m.ident for m in mods]:
                if sys.platform == 'win32':
                    line += ' -lws2_32'
                elif sys.platform == 'sunos5':
                    line += ' -lsocket -lnsl'
            if 'os' in [m.ident for m in mods]:
                if sys.platform not in ['win32', 'darwin', 'sunos5']:
                    line += ' -lutil'

        print >>makefile, line
    print >>makefile

    print >>makefile, 'all:\t'+ident+'\n'

    if not getgx().extension_module:
        print >>makefile, 'run:\tall'
        print >>makefile, '\t./'+ident+'\n'

    print >>makefile, 'CPPFILES='+cppfiles
    print >>makefile, 'HPPFILES='+hppfiles+'\n'

    _out = '-o '
    _ext=''
    if getgx().msvc:
        _out = '/out:'
        _ext = ''
        if not getgx().extension_module:
            _ext = '.exe'

    for suffix, options in [('', ''), ('_prof', '-pg -ggdb'), ('_debug', '-g -ggdb')]:
        print >>makefile, ident+suffix+':\t$(CPPFILES) $(HPPFILES)'
        print >>makefile, '\t$(CC) '+options+' $(CCFLAGS) $(CPPFILES) $(LFLAGS) '+_out+ident+suffix+_ext + '\n'

    ext = ''
    if sys.platform == 'win32':
        ext = '.exe'
    print >>makefile, 'clean:'
    print >>makefile, '\trm -f %s %s %s\n' % (ident+ext, ident+'_prof'+ext, ident+'_debug'+ext)

    print >>makefile, '.PHONY: all run clean\n'

    makefile.close()
