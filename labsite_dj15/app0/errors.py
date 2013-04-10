from django.template import Template, Context 

class UploadError(Exception):
    ErrTemplate = Template('<p>{{head}}:</p><pre>{{message}}</pre>')
    Head = 'Errors'
    code = 10
    def html(self):
        return self.ErrTemplate.render(Context({
            'head': self.Head,
            'message': str(self),
            }))

class FormatError(UploadError): 
    code = 11
    Head = 'Naming format error'

class CheckError(UploadError): 
    code = 12
    Head = 'Check error'

class CompileError(UploadError):
    code = 13
    Head = 'Compile error'
