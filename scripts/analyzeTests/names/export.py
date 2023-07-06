import readAll
import sys
args = sys.argv
if args[1] == 'pure':
    with open('./pure', 'w') as f:
        for i in readAll.pure:
            f.write('{}\n'.format(i))
if args[1] == 'checking':
    import sanityCheck
    pure1 = getattr(readAll, 'pure1')
    pure2 = getattr(readAll, 'pure2')
    sgDiff = sanityCheck.singleDiff(pure1, pure2)

    mess = getattr(readAll, 'mess2')

    junit = getattr(readAll, 'junit')

    f = open('./checking', 'w')

    f.write('{}\n'.format('#pure1: {}'.format(len(pure1))))
    f.write('{}\n'.format('#pure2: {}'.format(len(pure2))))

    f.write('{}\n'.format('#intersect: {}'.format(len(sgDiff[0]))))
    for i in sgDiff[0]:
        f.write('{}\n'.format(i))

    f.write('{}\n'.format('#only in 1: {}'.format(len(sgDiff[1]))))
    for i in sgDiff[1]:
        f.write('{}\n'.format(i))

    f.write('{}\n'.format('#only in 2: {}'.format(len(sgDiff[2]))))
    for i in sgDiff[2]:
        f.write('{}\n'.format(i))


    f.write('{}\n'.format('#mess: '))
    for i in mess:
        f.write('{}\n'.format(i))

    f.write('{}\n'.format('#junit: '))
    for i in junit:
        f.write('{}\n'.format(i))
    f.close()
