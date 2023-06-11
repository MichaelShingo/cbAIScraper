typeOfOpportunity = ['Composition', 'composer', 'compose', 'Flutist', 'Teacher', 'Teaching', 'teach', 'flute', 'alto flute', 'bass flute', 'french horn', 'clarinet', 'bass clarinet', 'english horn', 'cor anglais',  'cello', 'piano', 'violin', 'viola', 
            'drums', 'percussion', 'oboe', 'bassoon', 'guitar', 'instrumentalist', 'list all instruments', 'photography', 'volunteer', 'dance', 'dancing', 'instructor', 'visual artist', 'visual art',
            'music', 'project', 'interdisciplinary', 'musician', 'performance', 'performer', 'entrepreneur', 'student', 'for students', 'scholarship', 'jazz', 'tour', 'competition', 'administration', 'arts', 'education', 
            'workshop', 'presentation', 'commission', 'call for score', 'orchestra', 'string quartet', 'string', 'trio', 'duo', 'solo', 'soloist', 'prize', 'relief', 'adobe', 'singer', 'vocal', 'opera',
            'accordion', 'banjo', 'bagpipe', 'violoncello',  'guitar', 'piano', 'bass', 'double bass', 'bassoon', 'contrabassoon', 'cornet', 'erhu', 'fiddle', 'euphonium', 'glockenspiel', 'electric guitar', 'bass guitar',
            'acoustic guitar', 'classical guitar', 'guzheng', 'harmonica', 'harp', 'harpsichord', 'kalimba', 'lute', 'lyre', 'mandolin', 'marimba', 'melodica', 'organ', 'piccolo', 'recorder',  'saxophone'
            'steel pan', 'synthesizer', 'electronic', 'electronic music', 'timpani', 'trombone', 'bass trombone', 'trumpet', 'tuba', 'ukelele', 'viola d\'amore', 'xylophone', 'zither']
lowerCase = []

for word in typeOfOpportunity:
    lowerCase.append(word.casefold())


print(lowerCase)