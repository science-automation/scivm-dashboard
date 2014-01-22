# Copyright 2014 Science Automation
#
# This file is part of Science VM.
#
# Science VM is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Science VM is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Science VM. If not, see <http://www.gnu.org/licenses/>.

import itertools


class IntJID(object):
    
    def __init__(self, desc):
        self.desc = desc 

    @classmethod
    def check_valid(cls, desc):
        """
            >>> IntJID.check_valid(3)
            True
        """
        if isinstance(desc, int):
            return True
        return False
    
    def as_python(self):
        """
            >>> IntJID(3).as_python()
            3
        """
        return self.desc
    
    def __iter__(self):
        return iter([self.desc,])
    
    def __len__(self):
        return 1
    
    def top(self):
        return self.desc


class ListJIDS(object):
    
    def __init__(self, desc):
        if isinstance(desc, int):
            desc = [desc,]
        self.desc = desc 
        self.desc.sort()

    @classmethod
    def check_valid(cls, desc):
        """
            >>> ListJIDS.check_valid([])
            False
            >>> ListJIDS.check_valid([3])
            True
        """
        if isinstance(desc, list) and len(desc) > 0:
            f = lambda x: isinstance(x, int)
            return all(( f(x) for x in desc))
        return False
    
    def as_python(self):
        return self.desc

    def __iter__(self):
        return iter(self.desc)
    
    def __len__(self):
        return len(self.desc)
    
    def top(self):
        """
            >>> ListJIDS([11, 4, 23, 9]).top()
            23
        """
        return max(self.desc) #FIXME self.desc is sorted..
        

class XrangeJIDS(object):
     
    def __init__(self, desc):
        self.desc = desc
    
    @classmethod
    def check_valid(cls, desc):
        """ picloud xrange desc is the folowing:
            ['xrange', <from>, <step-by>, <elem-count>] 
            
            >>> XrangeJIDS.check_valid(['xrange', 1, 1, 2])
            True
            >>> XrangeJIDS.check_valid(['xrange', 1, 1])
            False
            >>> XrangeJIDS.check_valid([1, 1, 1])
            False
        """
        return isinstance(desc, list) and desc[0] == 'xrange' and len(desc) == 4 and all(itertools.imap(lambda x: isinstance(x, int), desc[1:]))
    
    def as_python(self):
        """ Python representation of the jids
            >>> XrangeJIDS(['xrange', 1, 1, 4]).as_python()
            xrange(1, 5)
            >>> XrangeJIDS(['xrange', 1, 2, 10]).as_python()
            xrange(1, 21, 2)
        """
        return xrange(self.desc[1], self.desc[1] + self.desc[2] * (self.desc[3]-1)+1, self.desc[2])
    
    def __iter__(self):
        """ 
            >>> list(XrangeJIDS(['xrange', 2, 1, 5]))
            [2, 3, 4, 5, 6]
        """
        return iter(self.as_python())
    
    def __len__(self):
        return self.desc[3]
    
    def top(self):
        """
            >>> XrangeJIDS(['xrange', 1, 1, 10]).top()
            10
            >>> XrangeJIDS(['xrange', 1, 2, 10]).top()
            19
        """
        return self.desc[1] + self.desc[2] * (self.desc[3]-1)


class ComplexJIDS(object):
    CLASSES = (IntJID, ListJIDS, XrangeJIDS)

    def __init__(self, desc):
        self.desc = desc
        self.objects = []
        for sub_desc in desc:
            self.objects.append(_get_jids_object(self.CLASSES, sub_desc))

    @classmethod
    def check_valid(cls, desc):
        """
            >>> ComplexJIDS.check_valid([1, ['xrange', 2, 1, 4], [6,11]])
            True
            >>> ComplexJIDS.check_valid([1, 6, 11])
            True
            >>> ComplexJIDS.check_valid(['xrange', 2, 1, 4])
            False
        """
        if desc:
            return all([ _get_jids_object(cls.CLASSES, sub_desc) for sub_desc in desc ])
        return None
    
    def as_python(self):
        """ Python representation of the jids
            >>> ComplexJIDS([1, ['xrange', 2, 1, 4], [6,11]]).as_python()
            [1, xrange(2, 6), [6, 11]]
        """
        return [ obj.as_python() for obj in self.objects ]
    
    def __iter__(self):
        """ 
            >>> list(ComplexJIDS([1, [6, 11], ['xrange', 2, 1, 4]]))
            [1, 6, 11, 2, 3, 4, 5]
        """
        return itertools.chain(*self.objects)
    
    def __len__(self):
        """
            >>> len(ComplexJIDS([1, ['xrange', 2, 1, 4], [6,11]]))
            7
        """
        return sum([ len(obj) for obj in self.objects ])
    
    def top(self):
        """
            >>> ComplexJIDS([1, [6, 11], ['xrange', 2, 1, 4]]).top()
            11
        """
        return max([ obj.top() for obj in self.objects ])


_m = lambda klass, desc: klass if klass.check_valid(desc) else None
_f = lambda klass: klass is not None
def _get_jids_object(CLASSES, desc):
    for klass in itertools.ifilter(_f, ( _m(x, desc) for x in CLASSES )):
        return klass(desc)
    return None


class JIDS(object):
    CLASSES = (IntJID, ListJIDS, XrangeJIDS, ComplexJIDS)

    def __init__(self, desc):
        self.obj = _get_jids_object(self.CLASSES, desc)
        if self.obj is None: 
            raise Exception("JIDS descriptor is invalid")
        
    @classmethod
    def check_valid(cls, desc):
        f = lambda klass: klass.check_valid(desc)
        return any( (f(x) for x in self.CLASSES) )

    def as_python(self):
        return self.obj.as_python()
    
    def __len__(self):
        return len(self.obj)
        
    def __iter__(self):
        return self.obj.__iter__()

    def __repr__(self):
        return "%s" % repr(self.obj.as_python())
    
    def serialize(self):
        return self.obj.desc
    
    def top(self):
        return self.obj.top()
