#include <vo-aacenc/voAAC.h>
#include <vo-aacenc/cmnMemory.h>

#include <stdio.h>

int main(void)
{
    VO_AUDIO_CODECAPI api = {0};
    VO_MEM_OPERATOR memory = {0};
    VO_CODEC_INIT_USERDATA user_data = {0};
    AACENC_PARAM parameters = {0};
    VO_HANDLE encoder = NULL;
    VO_CODECBUFFER input = {0};
    VO_CODECBUFFER output = {0};
    VO_AUDIO_OUTPUTINFO output_info = {0};
    unsigned char pcm[1024 * 2] = {0};
    unsigned char aac[20480] = {0};
    VO_S32 result = voGetAACEncAPI(&api);

    if (result != VO_ERR_NONE) {
        if (fprintf(stderr, "voGetAACEncAPI failed: %ld\n", (long)result) < 0) {
            return 3;
        }
        return 1;
    }
    if (api.Init == NULL || api.SetParam == NULL ||
        api.SetInputData == NULL || api.GetOutputData == NULL ||
        api.Uninit == NULL) {
        if (fputs("voGetAACEncAPI returned an incomplete function table\n",
                  stderr) == EOF) {
            return 3;
        }
        return 2;
    }

    memory.Alloc = cmnMemAlloc;
    memory.Copy = cmnMemCopy;
    memory.Free = cmnMemFree;
    memory.Set = cmnMemSet;
    memory.Check = cmnMemCheck;
    user_data.memflag = VO_IMF_USERMEMOPERATOR;
    user_data.memData = &memory;

    if (api.Init(&encoder, VO_AUDIO_CodingAAC, &user_data) != VO_ERR_NONE) {
        fputs("AAC encoder initialization failed\n", stderr);
        return 3;
    }

    parameters.sampleRate = 44100;
    parameters.bitRate = 64000;
    parameters.nChannels = 1;
    parameters.adtsUsed = 1;
    if (api.SetParam(encoder, VO_PID_AAC_ENCPARAM, &parameters) != VO_ERR_NONE) {
        fputs("AAC encoder parameter configuration failed\n", stderr);
        api.Uninit(encoder);
        return 4;
    }

    input.Buffer = pcm;
    input.Length = sizeof(pcm);
    if (api.SetInputData(encoder, &input) != VO_ERR_NONE) {
        fputs("AAC encoder rejected PCM input\n", stderr);
        api.Uninit(encoder);
        return 5;
    }

    output.Buffer = aac;
    output.Length = sizeof(aac);
    if (api.GetOutputData(encoder, &output, &output_info) != VO_ERR_NONE ||
        output.Length < 7 || aac[0] != 0xff || (aac[1] & 0xf0) != 0xf0) {
        fputs("AAC encoder did not produce a valid ADTS frame\n", stderr);
        api.Uninit(encoder);
        return 6;
    }

    if (api.Uninit(encoder) != VO_ERR_NONE) {
        fputs("AAC encoder shutdown failed\n", stderr);
        return 7;
    }

    if (puts("libvo-aacenc AAC encoding test: OK") == EOF) {
        return 8;
    }
    return 0;
}
